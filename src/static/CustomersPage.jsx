import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Search, ShoppingCart } from 'lucide-react'
import { Button } from '@/components/ui/button'

const CustomerCard = ({ customer, onEdit, onDelete }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{customer.name}</h3>
          {customer.phone_number && (
            <p className="text-sm text-gray-600 mt-1">الهاتف: {customer.phone_number}</p>
          )}
          {customer.email && (
            <p className="text-sm text-gray-600">البريد: {customer.email}</p>
          )}
        </div>
        <div className="flex items-center space-x-2 space-x-reverse">
          <Button variant="ghost" size="sm" onClick={() => onEdit(customer)}>
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => onDelete(customer)}>
            <Trash2 className="h-4 w-4 text-red-500" />
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">عدد المبيعات:</span>
          <span className="font-medium text-gray-900 mr-2">{customer.sales_count}</span>
        </div>
        {customer.total_purchases !== undefined && (
          <div>
            <span className="text-gray-500">إجمالي المشتريات:</span>
            <span className="font-medium text-gray-900 mr-2">{customer.total_purchases} ريال</span>
          </div>
        )}
      </div>
    </div>
  )
}

const CustomerForm = ({ customer, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: customer?.name || '',
    address: customer?.address || '',
    phone_number: customer?.phone_number || '',
    email: customer?.email || ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSave(formData)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {customer ? 'تعديل العميل' : 'إضافة عميل جديد'}
          </h2>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              اسم العميل *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              رقم الهاتف
            </label>
            <input
              type="text"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              البريد الإلكتروني
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              العنوان
            </label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleChange}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex justify-end space-x-3 space-x-reverse pt-4">
            <Button type="button" variant="outline" onClick={onCancel}>
              إلغاء
            </Button>
            <Button type="submit">
              {customer ? 'تحديث' : 'إضافة'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

const CustomersPage = () => {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState(null)

  useEffect(() => {
    fetchCustomers()
  }, [])

  const fetchCustomers = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/customers')
      const data = await response.json()
      setCustomers(data)
    } catch (error) {
      console.error('Error fetching customers:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveCustomer = async (customerData) => {
    try {
      const url = editingCustomer 
        ? `http://localhost:5000/api/customers/${editingCustomer.customer_id}`
        : 'http://localhost:5000/api/customers'
      
      const method = editingCustomer ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(customerData)
      })

      if (response.ok) {
        await fetchCustomers()
        setShowForm(false)
        setEditingCustomer(null)
      } else {
        const errorData = await response.json()
        alert(errorData.error)
      }
    } catch (error) {
      console.error('Error saving customer:', error)
    }
  }

  const handleDeleteCustomer = async (customer) => {
    if (window.confirm(`هل أنت متأكد من حذف العميل "${customer.name}"؟`)) {
      try {
        const response = await fetch(`http://localhost:5000/api/customers/${customer.customer_id}`, {
          method: 'DELETE'
        })

        if (response.ok) {
          await fetchCustomers()
        } else {
          const errorData = await response.json()
          alert(errorData.error)
        }
      } catch (error) {
        console.error('Error deleting customer:', error)
      }
    }
  }

  const filteredCustomers = customers.filter(customer => {
    const matchesSearch = customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         customer.phone_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         customer.email?.toLowerCase().includes(searchTerm.toLowerCase())
    
    return matchesSearch
  })

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
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
          <h1 className="text-2xl font-bold text-gray-900">إدارة العملاء</h1>
          <p className="text-gray-600 mt-1">إدارة معلومات العملاء وسجل مشترياتهم</p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="ml-2 h-4 w-4" />
          إضافة عميل
        </Button>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="البحث في العملاء (الاسم، الهاتف، البريد)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Customers Grid */}
      {filteredCustomers.length === 0 ? (
        <div className="text-center py-12">
          <Users className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد عملاء</h3>
          <p className="text-gray-500 mb-4">ابدأ بإضافة عملاء جدد</p>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="ml-2 h-4 w-4" />
            إضافة عميل جديد
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCustomers.map(customer => (
            <CustomerCard
              key={customer.customer_id}
              customer={customer}
              onEdit={(cust) => {
                setEditingCustomer(cust)
                setShowForm(true)
              }}
              onDelete={handleDeleteCustomer}
            />
          ))}
        </div>
      )}

      {/* Customer Form Modal */}
      {showForm && (
        <CustomerForm
          customer={editingCustomer}
          onSave={handleSaveCustomer}
          onCancel={() => {
            setShowForm(false)
            setEditingCustomer(null)
          }}
        />
      )}
    </div>
  )
}

export default CustomersPage

