import { Route, Routes } from "react-router-dom";
import AppLayout from "./AppLayout";
import AppsPage from "./pages/AppsPage";
import ChatPage from "./pages/ChatPage";
import DashboardPage from "./pages/DashboardPage";
import HelpPage from "./pages/HelpPage";
import InboxPage from "./pages/InboxPage";
import LogsPage from "./pages/LogsPage";
import SettingsPage from "./pages/SettingsPage";
import SkillsPage from "./pages/SkillsPage";
import ToolsPage from "./pages/ToolsPage";

export default function App() {
	return (
		<Routes>
			<Route element={<AppLayout />}>
				<Route path="/" element={<DashboardPage />} />
				<Route path="/inbox" element={<InboxPage />} />
				<Route path="/tools" element={<ToolsPage />} />
				<Route path="/skills" element={<SkillsPage />} />
				<Route path="/chat" element={<ChatPage />} />
				<Route path="/apps" element={<AppsPage />} />
				<Route path="/logs" element={<LogsPage />} />
				<Route path="/settings" element={<SettingsPage />} />
				<Route path="/help" element={<HelpPage />} />
			</Route>
		</Routes>
	);
}
