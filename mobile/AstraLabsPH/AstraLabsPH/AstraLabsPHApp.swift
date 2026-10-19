import SwiftUI
import Security

// AstraLabs PH • Native owner companion
// UI-first shell. No fabricated sales, embedded credentials, or executable agent claims.
@main
struct AstraLabsPHApp: App {
    @StateObject private var model = MissionModel()
    var body: some Scene {
        WindowGroup {
            MainShell(model: model)
                .tint(.black)
                .preferredColorScheme(.light)
                .task { await model.refresh() }
        }
    }
}

enum StudioStyle {
    static let ink = Color(red: 0.11, green: 0.12, blue: 0.12)
    static let secondary = Color(red: 0.45, green: 0.47, blue: 0.46)
    static let canvas = Color(red: 0.978, green: 0.98, blue: 0.978)
    static let stroke = Color(red: 0.91, green: 0.92, blue: 0.91)
    static let subdued = Color(red: 0.95, green: 0.955, blue: 0.95)
}
enum StudioTab: Hashable { case home, analytics, akame, tasks, more }
enum AnalyticsCategory: String, CaseIterable, Identifiable {
    case revenue = "Revenue", apps = "Apps", books = "KDP", social = "Social"
    var id: String { rawValue }
}

// This keychain stores only short-lived owner session tokens.
// Native passkey acquisition is a separate authenticated release gate.
enum SessionVault {
    static let service = "com.astralabsph.mission-control.session"
    static func read() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "owner",
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var result: CFTypeRef?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
              let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }
    static func save(_ token: String) {
        guard token.hasPrefix("ash_"), let data = token.data(using: .utf8) else { return }
        clear()
        let attributes: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "owner",
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]
        SecItemAdd(attributes as CFDictionary, nil)
    }
    static func clear() {
        let q: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "owner"
        ]
        SecItemDelete(q as CFDictionary)
    }
}

struct MobileSummary: Decodable {
    let ok: Bool
    let asOf: String?
    let apple: AppleSummary?
    let providers: [ProviderMetric]?
    let social: [SocialMetric]?
    let sourceErrors: [String:String]?
}
struct AppleSummary: Decodable {
    let windowStart: String?
    let groups: [AppleGroup]
    let status: String?
}
struct AppleGroup: Decodable, Identifiable {
    let currency: String
    let app: String
    let proceeds: Double
    let units: Double
    let latestPeriod: String
    let lastImported: String
    var id: String { app + ":" + currency }
}
struct ProviderMetric: Decodable, Identifiable {
    let provider: String
    let app: String?
    let metric: String
    let value: Double?
    let unit: String?
    let status: String?
    let periodStart: String?
    let periodEnd: String?
    let capturedAt: String?
    let source: String?
    var id: String { provider + ":" + (app ?? "all") + ":" + metric }
}
struct SocialMetric: Decodable, Identifiable {
    let network: String
    let metric: String
    let value: Double?
    let unit: String?
    let periodEnd: String?
    let capturedAt: String?
    let source: String?
    var id: String { network + ":" + metric }
}
struct AkashicData: Decodable {
    let ok: Bool
    let today: String?
    let asOf: String?
    let projects: [StudioProject]
    let tasks: [StudioTask]
    let checks: [TaskCheck]
}
struct StudioProject: Decodable, Identifiable {
    let id: String
    let slug: String?
    let name: String
    let area: String?
    let status: String?
    let nextAction: String?
}
struct StudioTask: Decodable, Identifiable {
    let id: String
    let title: String
    let area: String?
    let detail: String?
}
struct TaskCheck: Decodable {
    let taskId: String
    let done: Bool
}

enum Networking {
    static let endpoint = "https://cscqulbludoyzsgniits.supabase.co/functions/v1/"
    static func get<T: Decodable>(_ route: String, bearer: String, as type: T.Type) async throws -> T {
        guard let url = URL(string: endpoint + route) else { throw URLError(.badURL) }
        var request = URLRequest(url: url)
        request.setValue("Bearer " + bearer, forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.cachePolicy = .reloadIgnoringLocalAndRemoteCacheData
        request.timeoutInterval = 15
        let (body, response) = try await URLSession.shared.data(for: request)
        guard let response = response as? HTTPURLResponse else { throw URLError(.badServerResponse) }
        if response.statusCode == 401 { throw APIError.authenticationExpired }
        guard response.statusCode == 200 else { throw APIError.providerUnavailable }
        let parser = JSONDecoder()
        parser.keyDecodingStrategy = .convertFromSnakeCase
        return try parser.decode(type, from: body)
    }
}
enum APIError: Error { case authenticationExpired, providerUnavailable }

@MainActor
final class MissionModel: ObservableObject {
    @Published var summary: MobileSummary?
    @Published var akashic: AkashicData?
    @Published var isLoading = false
    @Published var status = "Private session required"
    @Published var lastChecked: Date?
    var isAuthenticated: Bool { SessionVault.read() != nil }
    var checks: Set<String> {
        Set((akashic?.checks ?? []).filter { $0.done }.map(\.taskId))
    }
    var openTasks: [StudioTask] { (akashic?.tasks ?? []).filter { !checks.contains($0.id) } }
    func refresh() async {
        guard !isLoading else { return }
        guard let token = SessionVault.read() else {
            status = "Native passkey enrollment pending"
            summary = nil; akashic = nil
            return
        }
        isLoading = true
        defer { isLoading = false }
        async let reports = Networking.get("astralabs-mobile-summary", bearer:token, as: MobileSummary.self)
        async let mission = Networking.get("astralabs-akashic?view=dashboard", bearer:token, as: AkashicData.self)
        let reportResult = await Result { try await reports }
        let missionResult = await Result { try await mission }
        summary = try? reportResult.get()
        akashic = try? missionResult.get()
        if summary != nil || akashic != nil {
            lastChecked = Date()
            status = summary == nil || akashic == nil ? "Partial source availability" : "Imported sources checked"
        } else {
            if case .failure(APIError.authenticationExpired) = reportResult {
                SessionVault.clear()
                status = "Session expired. Native passkey sign-in required."
            } else {
                status = "Reporting source unavailable"
            }
        }
    }
}

struct MainShell: View {
    @ObservedObject var model: MissionModel
    @State private var selected: StudioTab = .home
    var body: some View {
        TabView(selection: $selected) {
            Tab("Home", systemImage:"house", value:.home) { HomeScreen(model:model) }
            Tab("Analytics", systemImage:"chart.bar.xaxis", value:.analytics) { AnalyticsScreen(model:model) }
            Tab("AKAME", systemImage:"bubble.left.and.bubble.right", value:.akame) { AkameScreen(model:model, selected:$selected) }
            Tab("Tasks", systemImage:"checklist", value:.tasks) { TasksScreen(model:model) }
            Tab("More", systemImage:"slider.horizontal.3", value:.more) { MoreScreen(model:model) }
        }
        .background(StudioStyle.canvas)
    }
}

struct Screen<Content: View>: View {
    let eyebrow: String
    let heading: String
    let subheading: String
    @ViewBuilder var content: Content
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment:.leading, spacing:22) {
                    VStack(alignment:.leading, spacing:5) {
                        Text(eyebrow.uppercased()).font(.system(size:10,weight:.semibold)).tracking(1.5).foregroundStyle(StudioStyle.secondary)
                        Text(heading).font(.system(size:33,weight:.semibold,design:.default)).tracking(-1.2).foregroundStyle(StudioStyle.ink)
                        Text(subheading).font(.system(size:12)).foregroundStyle(StudioStyle.secondary)
                    }
                    .padding(.top,11)
                    content
                }
                .padding(.horizontal,18)
                .padding(.bottom,32)
            }
            .background(StudioStyle.canvas.ignoresSafeArea())
            .toolbar(.hidden, for:.navigationBar)
        }
    }
}

struct Panel<Content: View>: View {
    let title: String?
    @ViewBuilder var content: Content
    init(_ title: String? = nil,@ViewBuilder content: ()-> Content){self.title=title;self.content=content()}
    var body: some View {
        VStack(alignment:.leading,spacing:15) {
            if let title { Text(title).font(.system(size:15,weight:.semibold)).foregroundStyle(StudioStyle.ink) }
            content
        }
        .padding(18)
        .frame(maxWidth:.infinity,alignment:.leading)
        .background(.white,in:RoundedRectangle(cornerRadius:16))
        .overlay(RoundedRectangle(cornerRadius:16).stroke(StudioStyle.stroke,lineWidth:0.8))
    }
}

struct DataItem: View {
    let name:String; let value:String; let meta:String
    var body: some View {
        VStack(alignment:.leading,spacing:8) {
            Text(name).font(.system(size:11,weight:.medium)).foregroundStyle(StudioStyle.secondary)
            Text(value).font(.system(size:23,weight:.semibold)).tracking(-0.7).foregroundStyle(StudioStyle.ink).minimumScaleFactor(0.7).lineLimit(1)
            Text(meta).font(.system(size:10)).foregroundStyle(StudioStyle.secondary).lineLimit(2)
        }
        .frame(maxWidth:.infinity,alignment:.leading)
        .padding(15)
        .frame(minHeight:118,alignment:.topLeading)
        .background(.white,in:RoundedRectangle(cornerRadius:15))
        .overlay(RoundedRectangle(cornerRadius:15).stroke(StudioStyle.stroke,lineWidth:0.8))
    }
}

struct SourceLine: View {
    let title:String
    let detail:String
    let status:String?
    var body: some View {
        HStack(alignment:.top,spacing:10) {
            VStack(alignment:.leading,spacing:4) {
                Text(title).font(.system(size:13,weight:.medium)).foregroundStyle(StudioStyle.ink)
                Text(detail).font(.system(size:11)).foregroundStyle(StudioStyle.secondary).fixedSize(horizontal:false,vertical:true)
            }
            Spacer(minLength:4)
            if let status {
                Text(status).font(.system(size:10,weight:.medium)).foregroundStyle(StudioStyle.secondary)
                    .padding(.horizontal,7).padding(.vertical,5).background(StudioStyle.subdued,in:Capsule())
            }
        }.padding(.vertical,6)
    }
}

struct InfoNote: View {
    let title:String;let detail:String
    var body: some View {
        VStack(alignment:.leading,spacing:6){
            Text(title).font(.system(size:13,weight:.semibold))
            Text(detail).font(.system(size:11)).foregroundStyle(StudioStyle.secondary)
        }
        .frame(maxWidth:.infinity,alignment:.leading)
        .padding(14)
        .background(StudioStyle.subdued,in:RoundedRectangle(cornerRadius:11))
    }
}
func money(_ number: Double, _ currency:String)->String {
    number.formatted(.currency(code:currency).precision(.fractionLength(2)))
}

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
