import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "./pages/NotFound.tsx";
import { AuthProvider } from "./hooks/useAuthStore";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import OTP from "./pages/auth/OTP";

import ClientLayout from "./pages/client/ClientLayout";
import ClientDashboard from "./pages/client/ClientDashboard";
import SendMoney from "./pages/client/SendMoney";
import PayQR from "./pages/client/PayQR";
import CashOps from "./pages/client/CashOps";
import History from "./pages/client/History";

import MerchantLayout from "./pages/merchant/MerchantLayout";
import MerchantDashboard from "./pages/merchant/MerchantDashboard";
import MerchantQR from "./pages/merchant/MerchantQR";
import MerchantSales from "./pages/merchant/MerchantSales";
import MerchantWithdraw from "./pages/merchant/MerchantWithdraw";
import MerchantProfile from "./pages/merchant/MerchantProfile";

import AdminLayout from "./pages/admin/AdminLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminValidations from "./pages/admin/AdminValidations";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminTransactions from "./pages/admin/AdminTransactions";
import AdminReports from "./pages/admin/AdminReports";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/otp" element={<OTP />} />

            <Route element={<ProtectedRoute roles={["client"]} />}>
              <Route path="/client" element={<ClientLayout />}>
                <Route index element={<ClientDashboard />} />
                <Route path="envoyer" element={<SendMoney />} />
                <Route path="payer" element={<PayQR />} />
                <Route path="cash" element={<CashOps />} />
                <Route path="historique" element={<History />} />
              </Route>
            </Route>

            <Route element={<ProtectedRoute roles={["commercant"]} />}>
              <Route path="/commercant" element={<MerchantLayout />}>
                <Route index element={<MerchantDashboard />} />
                <Route path="qr" element={<MerchantQR />} />
                <Route path="ventes" element={<MerchantSales />} />
                <Route path="retrait" element={<MerchantWithdraw />} />
                <Route path="profil" element={<MerchantProfile />} />
              </Route>
            </Route>

            <Route element={<ProtectedRoute roles={["admin"]} />}>
              <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<AdminDashboard />} />
                <Route path="validations" element={<AdminValidations />} />
                <Route path="utilisateurs" element={<AdminUsers />} />
                <Route path="transactions" element={<AdminTransactions />} />
                <Route path="rapports" element={<AdminReports />} />
              </Route>
            </Route>

            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
