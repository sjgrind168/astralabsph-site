import SwiftUI

struct HomeScreen: View {
    @ObservedObject var model:MissionModel
    var apple:AppleGroup? { model.summary?.apple?.groups.first }
    var kdp:ProviderMetric? { model.summary?.providers?.first(where:{$0.provider=="kdp" && $0.metric=="royalties_usd"}) }
    var body:some View {
        Screen(eyebrow:"ASTRALABS PH / OWNER",heading:"Business pulse",subheading:"Your operation at a glance. No guessed figures.") {
            HStack(spacing:10) {
                DataItem(name:"Apple proceeds",value:apple.map{money($0.proceeds,$0.currency)} ?? "Unavailable",meta:apple.map{"30 days · through \($0.latestPeriod)"} ?? "Import not verified in this session")
                DataItem(name:"KDP royalties",value:kdp?.value.map{money($0,"USD")} ?? "Unavailable",meta:kdp.map{"Estimated · through \($0.periodEnd ?? "?")"} ?? "Importer not verified")
            }
            Panel("Attention") {
                if model.isAuthenticated, let tasks=model.akashic?.tasks {
                    if model.openTasks.isEmpty { SourceLine(title:"No open daily checks",detail:"Only source-verified checks count as complete.",status:"Reviewed") }
                    else { ForEach(Array(model.openTasks.prefix(4))) { task in
                        SourceLine(title:task.title,detail:task.detail ?? task.area ?? "Review pending",status:"Open")
                    }}
                    Text("\(tasks.count) tracked tasks · \(model.checks.count) checked").font(.system(size:10)).foregroundStyle(StudioStyle.secondary)
                } else {
                    InfoNote(title:"Protected business status",detail:"Sign in with the native owner passkey to read verified tasks. This design preview never exposes private records.")
                }
            }
            Panel("AKAME's business brief") {
                InfoNote(title:"Insights will be source-backed",detail:"AKAME will compare actual reporting periods, detect gaps and propose specific next actions. The cloud inference runner is not yet deployed.")
            }
            Panel("Source health") {
                SourceLine(title:"Reporting integrity",detail:model.status,status:model.lastChecked == nil ? "Pending":"Checked")
                if let last=model.lastChecked {
                    Text("Last checked \(last.formatted(date:.abbreviated,time:.shortened))").font(.system(size:10)).foregroundStyle(StudioStyle.secondary)
                }
                Button { Task { await model.refresh() } } label:{
                    HStack{Image(systemName:"arrow.clockwise");Text("Refresh sources")}
                        .font(.system(size:12,weight:.semibold)).frame(maxWidth:.infinity).padding(.vertical,12)
                }.buttonStyle(.bordered).tint(StudioStyle.ink).disabled(model.isLoading)
            }
        }
    }
}

