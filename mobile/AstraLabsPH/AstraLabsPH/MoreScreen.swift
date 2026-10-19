import SwiftUI

struct MoreScreen: View {
    @ObservedObject var model: MissionModel
    var body:some View {
        Screen(eyebrow:"OWNER SETTINGS",heading:"More",subheading:"Everything technical stays out of your daily workflow.") {
            Panel("Account and privacy") {
                SourceLine(title:"Owner authentication",detail:"Existing web passkey works; iOS native passkey setup must be certified before private API data can load.",status:"Pending")
                SourceLine(title:"Data on this device",detail:"Sensitive data requires a valid short-lived token in iOS Keychain; no embedded service credentials.",status:"Protected")
            }
            Panel("Intelligence") {
                SourceLine(title:"AKAME reasoning",detail:"High effort requested when supported, task-aware failover will be validated per provider.",status:"High")
                SourceLine(title:"Mac-off mode",detail:"Cloud read-only analytics and chat planned; Xcode and local browser actions wait for Mac.",status:"Pending")
            }
            Panel("Connections and source health") {
                SourceLine(title:"Source availability",detail:model.status,status:model.lastChecked == nil ? "Pending" : "Checked")
                SourceLine(title:"App reports",detail:"Apple sales, Play snapshots, AdMob, KDP; actual source dates stay visible.",status:"Audited")
                SourceLine(title:"Zero-budget guard",detail:"Do not use paid APIs or switch to billable model routes without authorization.",status:"Required")
            }
            Panel("Full archive") {
                Link(destination:URL(string:"https://www.astralabsph.com/command-center/")!){
                    Label("Open Akashic Command Center",systemImage:"arrow.up.right")
                        .font(.system(size:13,weight:.semibold))
                }
                Text("Detailed records, technical audit logs and protocol history stay in the original secure site.")
                    .font(.system(size:11)).foregroundStyle(StudioStyle.secondary)
            }
        }
    }
}
