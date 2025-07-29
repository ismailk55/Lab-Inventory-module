import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchProfile();
    }
  }, [token]);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API}/profile`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      logout();
    }
  };

  const login = async (employeeNumber, password) => {
    try {
      const response = await axios.post(`${API}/login`, {
        employee_number: employeeNumber,
        password: password
      });
      
      const { access_token, user: userData } = response.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Component
const Login = () => {
  const [employeeNumber, setEmployeeNumber] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(employeeNumber, password);
    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          {/* Logo */}
          <div className="mb-4">
            <img 
              src="https://customer-assets.emergentagent.com/job_lab-inventory-app/artifacts/vclfpmat_naqua%20logo%20full-thumbnail.png" 
              alt="NAQUA Logo" 
              className="mx-auto h-20 w-auto"
            />
          </div>
          
          {/* Title */}
          <h1 className="text-2xl font-bold text-gray-800 mb-2">CENTRAL ANALYTICAL SERVICES</h1>
          <h2 className="text-xl font-semibold text-blue-600 mb-2">Laboratory Inventory</h2>
          <p className="text-gray-600">Management System</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Employee Number
            </label>
            <input
              type="text"
              value={employeeNumber}
              onChange={(e) => setEmployeeNumber(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your employee number"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your password"
              required
            />
          </div>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Default Admin: ADMIN001 / admin123</p>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [categoryStats, setCategoryStats] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    fetchDashboardStats();
    fetchCategoryStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    }
  };

  const fetchCategoryStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/category-stats`);
      setCategoryStats(response.data);
    } catch (error) {
      console.error('Failed to fetch category stats:', error);
    }
  };

  if (!stats) {
    return <div className="flex justify-center items-center h-64">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600">Laboratory Inventory Overview</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <DashboardCard 
          title="Total Items"
          value={stats.total_items}
          color="blue"
          onClick={() => window.dashboardNavigation?.('inventory', 'all')}
        />
        
        <DashboardCard 
          title="Low Stock"
          value={stats.low_stock_items}
          color="red"
          onClick={() => window.dashboardNavigation?.('inventory', 'low_stock')}
        />
        
        <DashboardCard 
          title="Expiring Soon"
          value={stats.expiring_soon}
          color="yellow"
          onClick={() => window.dashboardNavigation?.('inventory', 'expiring_soon')}
        />
        
        <DashboardCard 
          title="Expired"
          value={stats.expired_items}
          color="gray"
          onClick={() => window.dashboardNavigation?.('inventory', 'expired')}
        />
        
        <DashboardCard 
          title="Pending Requests"
          value={stats.pending_requests}
          color="purple"
          onClick={() => window.dashboardNavigation?.('requests', 'pending')}
        />
      </div>

      {/* Category Stats */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Stock by Category</h3>
        <div className="space-y-2">
          {categoryStats.map((cat, index) => (
            <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
              <span className="font-medium">{cat._id}</span>
              <div className="text-sm text-gray-600">
                {cat.total_items} items • {cat.total_quantity} units
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Dashboard Card Component
const DashboardCard = ({ title, value, color, onClick }) => {
  const colorClasses = {
    blue: 'text-blue-600',
    red: 'text-red-600', 
    yellow: 'text-yellow-600',
    gray: 'text-gray-600',
    purple: 'text-purple-600'
  };

  return (
    <div 
      className="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg transition-shadow duration-200"
      onClick={onClick}
    >
      <div className={`text-2xl font-bold ${colorClasses[color]}`}>{value}</div>
      <div className="text-sm text-gray-600">{title}</div>
    </div>
  );
};

// Inventory Component
const Inventory = ({ initialFilter = 'all' }) => {
  const [items, setItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [currentFilter, setCurrentFilter] = useState(initialFilter);
  const { user } = useAuth();

  useEffect(() => {
    fetchInventory();
  }, []);

  useEffect(() => {
    applyFilter();
  }, [items, currentFilter]);

  const fetchInventory = async () => {
    try {
      const response = await axios.get(`${API}/inventory`);
      setItems(response.data);
    } catch (error) {
      console.error('Failed to fetch inventory:', error);
    }
  };

  const applyFilter = () => {
    let filtered = [...items];
    const now = new Date();
    const nextMonth = new Date();
    nextMonth.setMonth(nextMonth.getMonth() + 1);

    switch (currentFilter) {
      case 'low_stock':
        filtered = items.filter(item => item.quantity <= item.reorder_level);
        break;
      case 'zero_stock':
        filtered = items.filter(item => item.quantity === 0);
        break;
      case 'expiring_soon':
        filtered = items.filter(item => {
          if (!item.validity) return false;
          const validityDate = new Date(item.validity);
          return validityDate <= nextMonth && validityDate >= now;
        });
        break;
      case 'expired':
        filtered = items.filter(item => {
          if (!item.validity) return false;
          const validityDate = new Date(item.validity);
          return validityDate < now;
        });
        break;
      case 'all':
      default:
        filtered = items;
        break;
    }

    setFilteredItems(filtered);
  };

  const getFilterTitle = () => {
    switch (currentFilter) {
      case 'low_stock':
        return 'Low Stock Items';
      case 'below_reorder':
        return 'Below Reorder Level Items';
      case 'below_target':
        return 'Below Target Stock Level Items';
      case 'zero_stock':
        return 'Zero Stock Items';
      case 'expiring_soon':
        return 'Items Expiring Soon';
      case 'expired':
        return 'Expired Items';
      case 'all':
      default:
        return 'All Inventory Items';
    }
  };

  const getFilterDescription = () => {
    switch (currentFilter) {
      case 'low_stock':
        return 'Items that have reached or fallen below their reorder level';
      case 'below_reorder':
        return 'Items with quantity below the reorder level';
      case 'below_target':
        return 'Items with quantity below the target stock level';
      case 'zero_stock':
        return 'Items with zero quantity in stock';
      case 'expiring_soon':
        return 'Items expiring within the next month';
      case 'expired':
        return 'Items that have passed their validity date';
      case 'all':
      default:
        return 'Complete laboratory stock inventory';
    }
  };

  const downloadExcel = async () => {
    try {
      const response = await axios.get(`${API}/inventory/export/excel`, {
        params: { filter: currentFilter },
        responseType: 'blob', // Important for file download
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename with timestamp and filter
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      const filterSuffix = currentFilter !== 'all' ? `_${currentFilter}` : '';
      link.setAttribute('download', `inventory_export${filterSuffix}_${timestamp}.xlsx`);
      
      // Append to html link element page
      document.body.appendChild(link);
      
      // Start download
      link.click();
      
      // Clean up and remove the link
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Failed to download Excel file:', error);
      alert('Failed to download Excel file. Please try again.');
    }
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{getFilterTitle()}</h1>
          <p className="text-gray-600">{getFilterDescription()}</p>
        </div>
        <div className="flex space-x-3">
          {/* Filter Buttons */}
          <div className="flex flex-wrap space-x-2 space-y-1">
            <button
              onClick={() => setCurrentFilter('all')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'all'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setCurrentFilter('zero_stock')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'zero_stock'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Zero Stock
            </button>
            <button
              onClick={() => setCurrentFilter('below_reorder')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'below_reorder'
                  ? 'bg-orange-100 text-orange-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Below Reorder
            </button>
            <button
              onClick={() => setCurrentFilter('below_target')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'below_target'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Below Target
            </button>
            <button
              onClick={() => setCurrentFilter('low_stock')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'low_stock'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Low Stock
            </button>
            <button
              onClick={() => setCurrentFilter('expiring_soon')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'expiring_soon'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Expiring
            </button>
            <button
              onClick={() => setCurrentFilter('expired')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'expired'
                  ? 'bg-gray-100 text-gray-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Expired
            </button>
          </div>

          {/* Download Excel Button */}
          <button
            onClick={downloadExcel}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
          >
            <span>📊</span>
            <span>Download Excel</span>
          </button>
          
          {isAdmin && (
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Add New Item
            </button>
          )}
        </div>
      </div>

      {/* Results Summary */}
      <div className="text-sm text-gray-600">
        Showing {filteredItems.length} of {items.length} items
      </div>

      {/* Items Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reorder Level</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Validity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                {isAdmin && <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredItems.map((item) => {
                const isLowStock = item.quantity <= item.reorder_level;
                const isBelowReorder = item.quantity < item.reorder_level;
                const isBelowTarget = item.quantity < item.target_stock_level;
                const isZeroStock = item.quantity === 0;
                const isExpired = item.validity && new Date(item.validity) < new Date();
                const isExpiringSoon = item.validity && 
                  new Date(item.validity) <= new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) &&
                  new Date(item.validity) >= new Date();

                // Determine row background color based on priority
                let rowClassName = "hover:bg-gray-50";
                if (isExpired) {
                  rowClassName = "bg-red-800 text-white hover:bg-red-900"; // Dark red for expired
                } else if (isZeroStock) {
                  rowClassName = "bg-red-100 hover:bg-red-200"; // Light red for zero stock
                } else if (isBelowReorder) {
                  rowClassName = "bg-yellow-100 hover:bg-yellow-200"; // Light yellow for below reorder
                }

                return (
                  <tr key={item.id} className={rowClassName}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-inherit">{item.item_name}</div>
                      <div className={`text-sm ${isExpired ? 'text-gray-300' : 'text-gray-500'}`}>{item.catalogue_no}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-inherit">{item.category}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-inherit">{item.location}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${
                        isZeroStock ? 'text-red-600' : 
                        isBelowReorder ? 'text-yellow-700' : 
                        'text-inherit'
                      }`}>
                        {item.quantity}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-inherit">{item.uom}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-inherit">{item.reorder_level}</td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${isExpired ? 'text-red-300' : 'text-inherit'}`}>
                      {item.validity ? new Date(item.validity).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col space-y-1">
                        {isExpired && (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-200 text-red-900">
                            Expired
                          </span>
                        )}
                        {!isExpired && isExpiringSoon && (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                            Expiring Soon
                          </span>
                        )}
                        {isZeroStock && !isExpired && (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            Zero Stock
                          </span>
                        )}
                        {!isZeroStock && isBelowReorder && !isExpired && (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800">
                            Below Reorder
                          </span>
                        )}
                        {!isZeroStock && !isBelowReorder && isBelowTarget && !isExpired && !isExpiringSoon && (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                            Below Target
                          </span>
                        )}
                        {!isLowStock && !isExpired && !isExpiringSoon && !isBelowTarget && (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            In Stock
                          </span>
                        )}
                      </div>
                    </td>
                    {isAdmin && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => setEditingItem(item)}
                          className={`${
                            isExpired ? 'text-red-300 hover:text-red-100' : 'text-blue-600 hover:text-blue-900'
                          } mr-3`}
                        >
                          Edit
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {filteredItems.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">No items found matching the current filter.</p>
        </div>
      )}

      {/* Add/Edit Item Modal */}
      {(showAddForm || editingItem) && (
        <ItemFormModal
          item={editingItem}
          onClose={() => {
            setShowAddForm(false);
            setEditingItem(null);
          }}
          onSubmit={() => {
            fetchInventory();
            setShowAddForm(false);
            setEditingItem(null);
          }}
        />
      )}
    </div>
  );
};

// Item Form Modal Component
const ItemFormModal = ({ item, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    item_name: item?.item_name || '',
    category: item?.category || '',
    sub_category: item?.sub_category || '',
    location: item?.location || '',
    manufacturer: item?.manufacturer || '',
    supplier: item?.supplier || '',
    model: item?.model || '',
    uom: item?.uom || '',
    catalogue_no: item?.catalogue_no || '',
    quantity: item?.quantity || 0,
    target_stock_level: item?.target_stock_level || 0,
    reorder_level: item?.reorder_level || 0,
    validity: item?.validity ? new Date(item.validity).toISOString().split('T')[0] : '',
    use_case: item?.use_case || ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        quantity: parseInt(formData.quantity),
        target_stock_level: parseInt(formData.target_stock_level),
        reorder_level: parseInt(formData.reorder_level),
        validity: formData.validity ? new Date(formData.validity) : null
      };

      if (item) {
        await axios.put(`${API}/inventory/${item.id}`, payload);
      } else {
        await axios.post(`${API}/inventory`, payload);
      }
      
      onSubmit();
    } catch (error) {
      console.error('Failed to save item:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">
            {item ? 'Edit Item' : 'Add New Item'}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Item Name</label>
                <input
                  type="text"
                  value={formData.item_name}
                  onChange={(e) => setFormData({...formData, item_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sub Category</label>
                <input
                  type="text"
                  value={formData.sub_category}
                  onChange={(e) => setFormData({...formData, sub_category: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Manufacturer</label>
                <input
                  type="text"
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Supplier</label>
                <input
                  type="text"
                  value={formData.supplier}
                  onChange={(e) => setFormData({...formData, supplier: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                <input
                  type="text"
                  value={formData.model}
                  onChange={(e) => setFormData({...formData, model: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Unit of Measurement</label>
                <input
                  type="text"
                  value={formData.uom}
                  onChange={(e) => setFormData({...formData, uom: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Catalogue No.</label>
                <input
                  type="text"
                  value={formData.catalogue_no}
                  onChange={(e) => setFormData({...formData, catalogue_no: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                <input
                  type="number"
                  value={formData.quantity}
                  onChange={(e) => setFormData({...formData, quantity: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Target Stock Level</label>
                <input
                  type="number"
                  value={formData.target_stock_level}
                  onChange={(e) => setFormData({...formData, target_stock_level: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reorder Level</label>
                <input
                  type="number"
                  value={formData.reorder_level}
                  onChange={(e) => setFormData({...formData, reorder_level: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Validity Date</label>
                <input
                  type="date"
                  value={formData.validity}
                  onChange={(e) => setFormData({...formData, validity: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Use Case</label>
              <textarea
                value={formData.use_case}
                onChange={(e) => setFormData({...formData, use_case: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
                required
              />
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {item ? 'Update' : 'Add'} Item
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// User Management Component
const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };

  const deleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await axios.delete(`${API}/users/${userId}`);
        fetchUsers();
      } catch (error) {
        console.error('Failed to delete user:', error);
        alert('Failed to delete user');
      }
    }
  };

  const isAdmin = user?.role === 'admin';

  if (!isAdmin) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Access denied. Admin privileges required.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">User Management</h1>
          <p className="text-gray-600">Manage system users and their access levels</p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Add New User
        </button>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee Number</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Section</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((userItem) => (
                <tr key={userItem.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{userItem.full_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {userItem.employee_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {userItem.section}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      userItem.role === 'admin' 
                        ? 'bg-purple-100 text-purple-800' 
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {userItem.role.charAt(0).toUpperCase() + userItem.role.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {userItem.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(userItem.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {userItem.id !== user.id && (
                      <button
                        onClick={() => deleteUser(userItem.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add User Modal */}
      {showAddForm && (
        <UserFormModal
          onClose={() => setShowAddForm(false)}
          onSubmit={() => {
            fetchUsers();
            setShowAddForm(false);
          }}
        />
      )}
    </div>
  );
};

// User Form Modal Component
const UserFormModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    full_name: '',
    employee_number: '',
    section: '',
    role: 'user',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/register`, formData);
      onSubmit();
    } catch (error) {
      console.error('Failed to create user:', error);
      setError(error.response?.data?.detail || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full">
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">Add New User</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter full name"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Employee Number</label>
              <input
                type="text"
                value={formData.employee_number}
                onChange={(e) => setFormData({...formData, employee_number: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter employee number"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Section</label>
              <input
                type="text"
                value={formData.section}
                onChange={(e) => setFormData({...formData, section: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter section/department"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">User Level</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter email address"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter password"
                required
              />
            </div>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create User'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Withdrawal Requests Component
const WithdrawalRequests = ({ initialFilter = 'all' }) => {
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [inventory, setInventory] = useState([]);
  const [currentFilter, setCurrentFilter] = useState(initialFilter);
  const { user } = useAuth();

  useEffect(() => {
    fetchRequests();
    fetchInventory();
  }, []);

  useEffect(() => {
    applyFilter();
  }, [requests, currentFilter]);

  const fetchRequests = async () => {
    try {
      const response = await axios.get(`${API}/withdrawal-requests`);
      setRequests(response.data);
    } catch (error) {
      console.error('Failed to fetch requests:', error);
    }
  };

  const fetchInventory = async () => {
    try {
      const response = await axios.get(`${API}/inventory`);
      setInventory(response.data);
    } catch (error) {
      console.error('Failed to fetch inventory:', error);
    }
  };

  const applyFilter = () => {
    let filtered = [...requests];

    switch (currentFilter) {
      case 'pending':
        filtered = requests.filter(request => request.status === 'pending');
        break;
      case 'approved':
        filtered = requests.filter(request => request.status === 'approved');
        break;
      case 'rejected':
        filtered = requests.filter(request => request.status === 'rejected');
        break;
      case 'all':
      default:
        filtered = requests;
        break;
    }

    setFilteredRequests(filtered);
  };

  const processRequest = async (requestId, action, comments = '') => {
    try {
      await axios.post(`${API}/withdrawal-requests/process`, {
        request_id: requestId,
        action: action,
        comments: comments
      });
      fetchRequests();
    } catch (error) {
      console.error('Failed to process request:', error);
    }
  };

  const getFilterTitle = () => {
    switch (currentFilter) {
      case 'pending':
        return 'Pending Withdrawal Requests';
      case 'approved':
        return 'Approved Withdrawal Requests';
      case 'rejected':
        return 'Rejected Withdrawal Requests';
      case 'all':
      default:
        return 'All Withdrawal Requests';
    }
  };

  const getFilterDescription = () => {
    switch (currentFilter) {
      case 'pending':
        return 'Requests waiting for admin approval';
      case 'approved':
        return 'Requests that have been approved and processed';
      case 'rejected':
        return 'Requests that have been rejected';
      case 'all':
      default:
        return 'Complete list of material withdrawal requests';
    }
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{getFilterTitle()}</h1>
          <p className="text-gray-600">{getFilterDescription()}</p>
        </div>
        <div className="flex space-x-3">
          {/* Filter Buttons */}
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentFilter('all')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'all'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setCurrentFilter('pending')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'pending'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Pending
            </button>
            <button
              onClick={() => setCurrentFilter('approved')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'approved'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Approved
            </button>
            <button
              onClick={() => setCurrentFilter('rejected')}
              className={`px-3 py-1 text-sm rounded ${
                currentFilter === 'rejected'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Rejected
            </button>
          </div>
          
          <button
            onClick={() => setShowRequestForm(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
          >
            New Request
          </button>
        </div>
      </div>

      {/* Results Summary */}
      <div className="text-sm text-gray-600">
        Showing {filteredRequests.length} of {requests.length} requests
      </div>

      {/* Requests Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requested By</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Purpose</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                {isAdmin && <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredRequests.map((request) => (
                <tr key={request.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                    {request.item_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {request.requested_quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {request.requested_by_name}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {request.purpose}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      request.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      request.status === 'approved' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(request.created_at).toLocaleDateString()}
                  </td>
                  {isAdmin && request.status === 'pending' && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => processRequest(request.id, 'approve')}
                        className="text-green-600 hover:text-green-900 mr-3"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => processRequest(request.id, 'reject')}
                        className="text-red-600 hover:text-red-900"
                      >
                        Reject
                      </button>
                    </td>
                  )}
                  {isAdmin && request.status !== 'pending' && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <span className="text-gray-400">
                        {request.status === 'approved' ? 'Approved' : 'Rejected'}
                      </span>
                    </td>
                  )}
                  {!isAdmin && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <span className="text-gray-400">View Only</span>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredRequests.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">No requests found matching the current filter.</p>
        </div>
      )}

      {/* Request Form Modal */}
      {showRequestForm && (
        <RequestFormModal
          inventory={inventory}
          onClose={() => setShowRequestForm(false)}
          onSubmit={() => {
            fetchRequests();
            setShowRequestForm(false);
          }}
        />
      )}
    </div>
  );
};

// Request Form Modal Component
const RequestFormModal = ({ inventory, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    item_id: '',
    requested_quantity: 1,
    purpose: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/withdrawal-requests`, {
        ...formData,
        requested_quantity: parseInt(formData.requested_quantity)
      });
      onSubmit();
    } catch (error) {
      console.error('Failed to create request:', error);
      alert(error.response?.data?.detail || 'Failed to create request');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full">
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">New Withdrawal Request</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Select Item</label>
              <select
                value={formData.item_id}
                onChange={(e) => setFormData({...formData, item_id: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select an item</option>
                {inventory.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.item_name} (Available: {item.quantity} {item.uom})
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Requested Quantity</label>
              <input
                type="number"
                min="1"
                value={formData.requested_quantity}
                onChange={(e) => setFormData({...formData, requested_quantity: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Purpose</label>
              <textarea
                value={formData.purpose}
                onChange={(e) => setFormData({...formData, purpose: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
                placeholder="Describe the purpose of this request..."
                required
              />
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Submit Request
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Main Layout Component
const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [pageProps, setPageProps] = useState({});

  // Set up global navigation function for dashboard cards
  useEffect(() => {
    window.dashboardNavigation = (page, filter) => {
      setCurrentPage(page);
      setPageProps(filter ? { initialFilter: filter } : {});
    };
    
    return () => {
      delete window.dashboardNavigation;
    };
  }, []);

  const navigation = [
    { id: 'dashboard', name: 'Dashboard', icon: '📊' },
    { id: 'inventory', name: 'Inventory', icon: '📦' },
    { id: 'requests', name: 'Requests', icon: '📋' },
    ...(user?.role === 'admin' ? [{ id: 'users', name: 'Users', icon: '👥' }] : []),
  ];

  const handleNavigation = (pageId) => {
    setCurrentPage(pageId);
    setPageProps({}); // Reset page props when navigating via sidebar
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'inventory':
        return <Inventory {...pageProps} />;
      case 'requests':
        return <WithdrawalRequests {...pageProps} />;
      case 'users':
        return <UserManagement />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img 
                src="https://customer-assets.emergentagent.com/job_lab-inventory-app/artifacts/vclfpmat_naqua%20logo%20full-thumbnail.png" 
                alt="NAQUA Logo" 
                className="h-8 w-auto mr-3"
              />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">CENTRAL ANALYTICAL SERVICES</h1>
                <p className="text-sm text-gray-600">Laboratory Inventory System</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                {user?.full_name} ({user?.section}) - {user?.role}
              </span>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <nav className="w-64 bg-white rounded-lg shadow p-6">
            <ul className="space-y-2">
              {navigation.map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => handleNavigation(item.id)}
                    className={`w-full flex items-center px-3 py-2 text-left rounded-md transition-colors ${
                      currentPage === item.id
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <span className="mr-3">{item.icon}</span>
                    {item.name}
                  </button>
                </li>
              ))}
            </ul>
          </nav>

          {/* Main Content */}
          <main className="flex-1">
            {children || renderPage()}
          </main>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </div>
  );
}

const AppContent = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Login />;
  }

  return <Layout />;
};

export default App;