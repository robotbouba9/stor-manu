import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Package } from 'lucide-react'
import { Button } from '@/components/ui/button'

const CategoryCard = ({ category, onEdit, onDelete }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
          <p className="text-sm text-gray-600 mt-1">
            عدد المنتجات: {category.products_count}
          </p>
        </div>
        <div className="flex items-center space-x-2 space-x-reverse">
          <Button variant="ghost" size="sm" onClick={() => onEdit(category)}>
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => onDelete(category)}>
            <Trash2 className="h-4 w-4 text-red-500" />
          </Button>
        </div>
      </div>
    </div>
  )
}

const CategoryForm = ({ category, onSave, onCancel }) => {
  const [name, setName] = useState(category?.name || '')

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSave({ name })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          {category ? 'تعديل الفئة' : 'إضافة فئة جديدة'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              اسم الفئة *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end space-x-3 space-x-reverse">
            <Button type="button" variant="outline" onClick={onCancel}>
              إلغاء
            </Button>
            <Button type="submit">
              {category ? 'تحديث' : 'إضافة'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

const CategoriesPage = () => {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingCategory, setEditingCategory] = useState(null)

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/categories')
      const data = await response.json()
      setCategories(data)
    } catch (error) {
      console.error('Error fetching categories:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveCategory = async (categoryData) => {
    try {
      const url = editingCategory 
        ? `http://localhost:5000/api/categories/${editingCategory.category_id}`
        : 'http://localhost:5000/api/categories'
      
      const method = editingCategory ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(categoryData)
      })

      if (response.ok) {
        await fetchCategories()
        setShowForm(false)
        setEditingCategory(null)
      } else {
        const errorData = await response.json()
        alert(errorData.error)
      }
    } catch (error) {
      console.error('Error saving category:', error)
    }
  }

  const handleDeleteCategory = async (category) => {
    if (window.confirm(`هل أنت متأكد من حذف الفئة "${category.name}"؟`)) {
      try {
        const response = await fetch(`http://localhost:5000/api/categories/${category.category_id}`, {
          method: 'DELETE'
        })

        if (response.ok) {
          await fetchCategories()
        } else {
          const errorData = await response.json()
          alert(errorData.error)
        }
      } catch (error) {
        console.error('Error deleting category:', error)
      }
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
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
          <h1 className="text-2xl font-bold text-gray-900">إدارة الفئات</h1>
          <p className="text-gray-600 mt-1">إدارة فئات المنتجات</p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="ml-2 h-4 w-4" />
          إضافة فئة
        </Button>
      </div>

      {/* Categories Grid */}
      {categories.length === 0 ? (
        <div className="text-center py-12">
          <Package className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد فئات</h3>
          <p className="text-gray-500 mb-4">ابدأ بإضافة فئات جديدة للمنتجات</p>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="ml-2 h-4 w-4" />
            إضافة فئة جديدة
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map(category => (
            <CategoryCard
              key={category.category_id}
              category={category}
              onEdit={(cat) => {
                setEditingCategory(cat)
                setShowForm(true)
              }}
              onDelete={handleDeleteCategory}
            />
          ))}
        </div>
      )}

      {/* Category Form Modal */}
      {showForm && (
        <CategoryForm
          category={editingCategory}
          onSave={handleSaveCategory}
          onCancel={() => {
            setShowForm(false)
            setEditingCategory(null)
          }}
        />
      )}
    </div>
  )
}

export default CategoriesPage

