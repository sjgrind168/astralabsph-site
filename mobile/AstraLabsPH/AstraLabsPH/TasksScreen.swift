import SwiftUI

struct TasksScreen: View {
    @ObservedObject var model: MissionModel
    @State private var filter: Int = 0
    var body: some View {
        Screen(eyebrow:"WORK THAT MOVES FORWARD",heading:"Missions",subheading:"Simple priorities and genuine execution receipts.") {
            Picker("Status",selection:$filter){
                Text("Open").tag(0);Text("Approval").tag(1);Text("Done").tag(2)
            }.pickerStyle(.segmented)
            Panel(filter == 0 ? "Open work" : filter == 1 ? "Waiting approval" : "Verified checks") {
                if filter == 1 {
                    InfoNote(title:"Approval queue not live",detail:"Approval must bind to an exact operation, recipient and risk level. No unattended worker has been deployed yet.")
                } else {
                    let items = (model.akashic?.tasks ?? []).filter {
                        filter == 2 ? model.checks.contains($0.id) : !model.checks.contains($0.id)
                    }
                    if items.isEmpty {
                        InfoNote(title:model.akashic == nil ? "Private source unavailable" : "Nothing to display",
                                 detail:model.akashic == nil ? "Authenticate to load real tasks." : "No matching verified tasks in this view.")
                    }
                    ForEach(items) { task in
                        SourceLine(title:task.title,detail:task.detail ?? task.area ?? "",
                                   status:filter==2 ? "Checked" : "Open")
                    }
                }
            }
            Panel("ASTRA ↔ AKAME inbox") {
                SourceLine(title:"Shared Akashic handoffs",detail:"Agents publish authenticated versioned messages. This app will present the relevant thread in its mission details.",status:"Website live")
                Link(destination:URL(string:"https://www.astralabsph.com/command-center/")!) {
                    Label("Open detailed Command Center",systemImage:"arrow.up.right")
                        .font(.system(size:12,weight:.semibold))
                }
            }
        }
    }
}

