import { useState, useEffect } from 'react'
import { 
  Package, 
  Users, 
  ShoppingCart, 
  TrendingUp,
  AlertTriangle,
  DollarSign
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const StatCard = ({ title, value, icon: Icon, color = 'blue', trend = null }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && (
            <p className={`text-sm mt-1 ${trend.positive ? 'text-green-600' : 'text-red-600'}`}>
              {trend.value}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-full bg-${color}-50`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
      </div>
    </div>
  )
}

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalCustomers: 0,
    todaySales: 0,
    todayRevenue: 0,
    lowStockProducts: []
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // جلب إحصائيات المنتجات
        const productsResponse = await fetch('http://localhost:5000/api/products')
        const products = await productsResponse.json()

        // جلب إحصائيات العملاء
        const customersResponse = await fetch('http://localhost:5000/api/customers')
        const customers = await customersResponse.json()

        // جلب إحصائيات المبيعات
        const salesStatsResponse = await fetch('http://localhost:5000/api/sales/stats')
        const salesStats = await salesStatsResponse.json()

        // جلب المنتجات ذات المخزون المنخفض
        const lowStockResponse = await fetch('http://localhost:5000/api/products/low-stock')
        const lowStockProducts = await lowStockResponse.json()

        setStats({
          totalProducts: products.length,
          totalCustomers: customers.length,
          todaySales: salesStats.today_sales || 0,
          todayRevenue: salesStats.today_revenue || 0,
          lowStockProducts: lowStockProducts
        })
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-32 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">لوحة التحكم</h1>
          <p className="text-gray-600 mt-1">نظرة عامة على أداء المحل</p>
        </div>
        <Button>
          <ShoppingCart className="ml-2 h-4 w-4" />
          مبيعة جديدة
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="إجمالي المنتجات"
          value={stats.totalProducts}
          icon={Package}
          color="blue"
        />
        <StatCard
          title="إجمالي العملاء"
          value={stats.totalCustomers}
          icon={Users}
          color="green"
        />
        <StatCard
          title="مبيعات اليوم"
          value={stats.todaySales}
          icon={ShoppingCart}
          color="purple"
        />
        <StatCard
          title="إيرادات اليوم"
          value={`${stats.todayRevenue.toLocaleString()} ريال`}
          icon={DollarSign}
          color="yellow"
        />
      </div>

      {/* Low Stock Alert */}
      {stats.lowStockProducts.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <AlertTriangle className="h-5 w-5 text-yellow-600 ml-2" />
            <h3 className="text-lg font-semibold text-yellow-800">
              تنبيه: منتجات بمخزون منخفض
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {stats.lowStockProducts.map((product) => (
              <div key={product.product_id} className="bg-white rounded-lg p-4 border border-yellow-200">
                <h4 className="font-medium text-gray-900">{product.name}</h4>
                <p className="text-sm text-gray-600 mt-1">
                  {product.brand} {product.model}
                </p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-sm text-red-600 font-medium">
                    الكمية: {product.quantity}
                  </span>
                  <span className="text-xs text-gray-500">
                    الحد الأدنى: {product.min_stock_level}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <Button variant="outline" size="sm">
              عرض جميع المنتجات
            </Button>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">إجراءات سريعة</h3>
          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              <Package className="ml-2 h-4 w-4" />
              إضافة منتج جديد
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Users className="ml-2 h-4 w-4" />
              إضافة عميل جديد
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <ShoppingCart className="ml-2 h-4 w-4" />
              إنشاء فاتورة
            </Button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">المبيعات الأخيرة</h3>
          <div className="text-center text-gray-500 py-8">
            <ShoppingCart className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>لا توجد مبيعات حديثة</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">المنتجات الأكثر مبيعاً</h3>
          <div className="text-center text-gray-500 py-8">
            <TrendingUp className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>لا توجد بيانات كافية</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

