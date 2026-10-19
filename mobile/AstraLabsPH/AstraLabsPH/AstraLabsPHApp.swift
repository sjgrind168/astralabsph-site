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
        summary = try? await reports
        akashic = try? await mission
        if summary != nil || akashic != nil {
            lastChecked = Date()
            status = summary == nil || akashic == nil ? "Partial source availability" : "Imported sources checked"
        } else {
            status = "Unable to load private sources; check the session or connectivity."
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

