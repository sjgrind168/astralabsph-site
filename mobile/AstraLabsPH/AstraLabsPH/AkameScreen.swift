import SwiftUI

struct AkameScreen: View {
    @ObservedObject var model: MissionModel
    @Binding var selected: StudioTab
    @State private var draft = ""
    var body: some View {
        Screen(eyebrow:"YOUR AI BUSINESS ALLY",heading:"AKAME",subheading:"Strategy, analysis, research and coordinated missions.") {
            Panel(nil) {
                HStack {
                    Image(systemName:"circle.hexagongrid").font(.system(size:26)).frame(width:42,height:42)
                        .background(StudioStyle.subdued,in:RoundedRectangle(cornerRadius:12))
                    VStack(alignment:.leading,spacing:3){
                        Text("AKAME").font(.system(size:14,weight:.semibold))
                        Text("High reasoning requested · fallback audited").font(.system(size:10)).foregroundStyle(StudioStyle.secondary)
                    }
                    Spacer()
                    Text("Cloud pending").font(.system(size:10)).foregroundStyle(StudioStyle.secondary)
                }
                Divider()
                InfoNote(title:"Business companion preview",detail:"Your Mac assistant's memory and coding specialist are preserved. Cloud chat and automatic ASTRA handoff need the secured runner before this input can send real messages.")
                TextField("Ask AKAME about your business…",text:$draft,axis:.vertical)
                    .lineLimit(2...5).textFieldStyle(.roundedBorder).disabled(true)
                    .accessibilityHint("Disabled until cloud AKAME authentication and inference are verified.")
                Button("Open current missions") { selected = .tasks }
                    .font(.system(size:12,weight:.semibold)).buttonStyle(.bordered)
            }
            Panel("Ways AKAME will help") {
                SourceLine(title:"Explain the numbers",detail:"Compare comparable periods, explain what changed and cite sources",status:nil)
                SourceLine(title:"Build a strategy",detail:"Assess apps, affiliate offers and KDP opportunities",status:nil)
                SourceLine(title:"Coordinate with ASTRA",detail:"Create an authenticated shared inbox mission and track its reply",status:nil)
                SourceLine(title:"Execute an approved task",detail:"Claim work only through a signed worker with exact action approval",status:nil)
            }
        }
    }
}

