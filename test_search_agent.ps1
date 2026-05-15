$token = (az account get-access-token --resource "https://ai.azure.com" --query accessToken -o tsv 2>$null)
$h = @{"Authorization"="Bearer $token";"Content-Type"="application/json"}
$base = "https://hr-concierge-ai.services.ai.azure.com/api/projects/hr-concierge-project"
$av = "api-version=2025-05-01"
$agentId = "asst_PRduntIyCvJgvkvcc7y4bqSB"
$searchKey = $env:AZURE_SEARCH_ADMIN_KEY
if (-not $searchKey) { Write-Error "Set AZURE_SEARCH_ADMIN_KEY env var"; exit 1 }

# Create thread and send message
$t = (Invoke-RestMethod -Uri "$base/threads?$av" -Headers $h -Method Post -Body '{}').id
Invoke-RestMethod -Uri "$base/threads/$t/messages?$av" -Headers $h -Method Post -Body '{"role":"user","content":"Can you search the knowledge base for information about the employee grievance escalation timeline and what happens after an ERLR investigation is completed?"}' | Out-Null
$run = Invoke-RestMethod -Uri "$base/threads/$t/runs?$av" -Headers $h -Method Post -Body "{`"assistant_id`":`"$agentId`"}"
$r = $run.id
Write-Host "Run: $r"

for($i=0; $i -lt 30; $i++){
    Start-Sleep 3
    $run = Invoke-RestMethod -Uri "$base/threads/$t/runs/$r`?$av" -Headers $h -Method Get
    Write-Host "  Status: $($run.status)"
    
    if($run.status -eq "requires_action"){
        $toolCalls = $run.required_action.submit_tool_outputs.tool_calls
        $outputs = @()
        foreach($tc in $toolCalls){
            $fn = $tc.function.name
            $args = $tc.function.arguments | ConvertFrom-Json
            Write-Host "  -> Calling: $fn"
            
            if($fn -eq "search_hr_knowledge_base"){
                $searchH = @{"api-key"=$searchKey;"Content-Type"="application/json"}
                $topK = if($args.top_results){[int]$args.top_results}else{3}
                $searchBody = @{search=$args.query;queryType="semantic";semanticConfiguration="hr-semantic-config";top=$topK;select="title,content,source"} | ConvertTo-Json
                $searchResult = Invoke-RestMethod -Uri "https://hr-concierge-search.search.windows.net/indexes/hr-knowledge-base/docs/search?api-version=2024-07-01" -Headers $searchH -Method Post -Body $searchBody
                $resultText = ""
                foreach($doc in $searchResult.value){
                    $snippet = $doc.content
                    if($snippet.Length -gt 500){ $snippet = $snippet.Substring(0, 500) + "..." }
                    $resultText += "## $($doc.title)`n$snippet`nSource: $($doc.source)`n---`n"
                }
                Write-Host "  <- Search returned $($searchResult.value.Count) docs"
                $outputs += @{tool_call_id=$tc.id; output=$resultText}
            }
            elseif($fn -eq "get_change_type_guidance"){
                $ct = $args.change_type
                $tier = if($ct -in @("emergency_contact","home_address","preferred_name","personal_info")){"ESS"}else{"Complex"}
                $link = if($tier -eq "ESS"){"https://workday.contoso.com/ess/personal-data"}else{"https://workday.contoso.com/hr-service-center/complex-changes"}
                $time = if($tier -eq "ESS"){"Immediate"}else{"3-5 business days"}
                $outputs += @{tool_call_id=$tc.id; output="{`"change_type`":`"$ct`",`"tier`":`"$tier`",`"timeline`":`"$time`",`"deep_link`":`"$link`"}"}
            }
            elseif($fn -eq "screen_grievance"){
                $cat = $args.concern_category
                $formal = @("harassment","discrimination","retaliation","bullying","threats_violence","ethical_violation","safety","accommodation")
                $path = if($cat -in $formal){"ERLR"}else{"GOOS"}
                $link = if($path -eq "ERLR"){"https://workday.contoso.com/erlr/intake"}else{"https://workday.contoso.com/goos/request"}
                $outputs += @{tool_call_id=$tc.id; output="{`"path`":`"$path`",`"deep_link`":`"$link`"}"}
            }
        }
        $submitBody = @{tool_outputs=$outputs} | ConvertTo-Json -Depth 5
        Invoke-RestMethod -Uri "$base/threads/$t/runs/$r/submit_tool_outputs?$av" -Headers $h -Method Post -Body $submitBody | Out-Null
        Write-Host "  Tool outputs submitted"
    }
    elseif($run.status -notin @("queued","in_progress")){break}
}

if($run.status -eq "completed"){
    $msgs = Invoke-RestMethod -Uri "$base/threads/$t/messages?$av" -Headers $h -Method Get
    Write-Host "`n=== AGENT RESPONSE (SEARCH-GROUNDED) ==="
    ($msgs.data | Where-Object {$_.role -eq "assistant"})[0].content[0].text.value
} else {
    Write-Host "FAILED: $($run.last_error.message)"
}
