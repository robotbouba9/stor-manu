import { useState } from 'react'
import { 
  Home, 
  Package, 
  Users, 
  Truck, 
  ShoppingCart, 
  BarChart3, 
  Settings, 
  Menu,
  X,
  Store
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const Layout = ({ children, currentPage = 'dashboard', onPageChange }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const menuItems = [
    { id: 'dashboard', label: 'الرئيسية', icon: Home },
    { id: 'products', label: 'المنتجات', icon: Package },
    { id: 'categories', label: 'الفئات', icon: Package },
    { id: 'customers', label: 'العملاء', icon: Users },
    { id: 'suppliers', label: 'الموردين', icon: Truck },
    { id: 'sales', label: 'المبيعات', icon: ShoppingCart },
    { id: 'reports', label: 'التقارير', icon: BarChart3 },
    { id: 'settings', label: 'الإعدادات', icon: Settings },
  ]

  const handleNavigation = (pageId) => {
    if (onPageChange) {
      onPageChange(pageId)
    }
    setSidebarOpen(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex" dir="rtl">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 right-0 z-50 w-64 bg-white shadow-lg transform ${
        sidebarOpen ? 'translate-x-0' : 'translate-x-full'
      } transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center space-x-3 space-x-reverse">
            <Store className="h-8 w-8 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">محل الهواتف</h1>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-3">
          <ul className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = currentPage === item.id
              
              return (
                <li key={item.id}>
                  <button
                    onClick={() => handleNavigation(item.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                        : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    <Icon className={`ml-3 h-5 w-5 ${isActive ? 'text-blue-700' : 'text-gray-400'}`} />
                    {item.label}
                  </button>
                </li>
              )
            })}
          </ul>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 lg:mr-64">
        {/* Top Bar */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-6">
            <Button
              variant="ghost"
              size="sm"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="text-sm text-gray-600">
                مرحباً بك في نظام إدارة المخزون
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          {children}
        </main>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default Layout

