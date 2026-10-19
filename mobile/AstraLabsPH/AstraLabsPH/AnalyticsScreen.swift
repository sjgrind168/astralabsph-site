import SwiftUI

struct AnalyticsScreen: View {
    @ObservedObject var model: MissionModel
    @State private var category: AnalyticsCategory = .revenue
    var body: some View {
        Screen(eyebrow:"BUSINESS INTELLIGENCE",heading:"Analytics",subheading:"Sales, installs, books and marketing by source.") {
            Picker("Analytics area",selection:$category) {
                ForEach(AnalyticsCategory.allCases){Text($0.rawValue).tag($0)}
            }.pickerStyle(.segmented)
            switch category {
            case .revenue:
                Panel("Apple developer proceeds") {
                    if let groups=model.summary?.apple?.groups, !groups.isEmpty {
                        ForEach(groups) { r in
                            SourceLine(title:r.app.capitalized+" · "+money(r.proceeds,r.currency),detail:"Units \(r.units.formatted()) · reporting through \(r.latestPeriod)",status:"Imported")
                        }
                    } else {InfoNote(title:"No verified Apple proceeds data loaded",detail:"No value is shown until the authenticated importer responds. Missing is not zero.") }
                }
                Panel("Other money sources") {
                    ForEach((model.summary?.providers ?? []).filter{$0.provider=="kdp" && $0.metric=="royalties_usd" || $0.provider=="google_play" && $0.metric=="payout_balance_usd" || $0.provider=="admob" && $0.metric=="estimated_earnings_usd"}) { row in
                        SourceLine(title:"\(row.provider.uppercased()) · \(row.metric.replacingOccurrences(of:"_",with:" "))",
                          detail:(row.value.map{money($0,row.unit ?? "USD")} ?? "Unavailable") + " · \(row.status ?? "unknown") · through \(row.periodEnd ?? "?")",
                          status:row.capturedAt == nil ? "No source" : "Historical")
                    }
                    if (model.summary?.providers ?? []).isEmpty {InfoNote(title:"Source records unavailable",detail:"KDP estimates, Play balances and ad income are not combined into fake total revenue.")}
                }
            case .apps:
                Panel("App performance") {
                    ForEach((model.summary?.providers ?? []).filter{$0.provider=="google_play" || $0.provider=="app_store_connect"}) { row in
                        SourceLine(title:"\((row.app ?? "all").capitalized) · \(row.metric.replacingOccurrences(of:"_",with:" "))",
                                   detail:"\(row.value?.formatted() ?? "Unavailable") \(row.unit ?? "") · through \(row.periodEnd ?? "unknown")",
                                   status:row.provider=="google_play" ? "Play" : "Apple")
                    }
                    if model.summary?.providers?.isEmpty ?? true {Text("No authenticated report loaded").font(.footnote).foregroundStyle(StudioStyle.secondary)}
                }
            case .books:
                Panel("KDP reporting") {
                    let books=(model.summary?.providers ?? []).filter{$0.provider=="kdp"}
                    if books.isEmpty {InfoNote(title:"KDP report unavailable",detail:"Royalty estimates and units appear only when the existing importer provides dated source data.")}
                    else { ForEach(books){row in
                        SourceLine(title:row.metric.replacingOccurrences(of:"_",with:" ").capitalized,
                                   detail:"\(row.value?.formatted() ?? "Unavailable") \(row.unit ?? "") · through \(row.periodEnd ?? "?")",
                                   status:row.status)
                    }}
                }
            case .social:
                Panel("Social reporting") {
                    let socials=model.summary?.social ?? []
                    if socials.isEmpty {InfoNote(title:"No social snapshot loaded",detail:"Only dated native/provider-sourced statistics will appear here.")}
                    else {ForEach(Array(socials.prefix(35))) {row in
                        SourceLine(title:row.network.capitalized+" · "+row.metric.replacingOccurrences(of:"_",with:" "),
                                   detail:"\(row.value?.formatted() ?? "Unavailable") \(row.unit ?? "") · through \(row.periodEnd ?? "?")",
                                   status:"Snapshot")
                    }}
                }
            }
            InfoNote(title:"Never mix unlike financial data",detail:"App Store proceeds, Play payout balance, customer gross, estimated KDP royalties and AdMob earnings have different meanings, currencies and reporting periods.")
        }
    }
}

