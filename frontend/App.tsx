import React, { useState, useEffect } from "react";

function App() {
  const [currentPage, setCurrentPage] = useState("home");

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return (
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            {/* Header */}
            <nav className="bg-white shadow-lg">
              <div className="max-w-7xl mx-auto px-4">
                <div className="flex justify-between items-center h-16">
                  <div className="flex items-center">
                    <h1 className="text-2xl font-bold text-blue-600">🏛️ Seva Sindhu</h1>
                  </div>
                  <div className="flex space-x-4">
                    <button
                      onClick={() => handleNavigate("home")}
                      className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600"
                    >
                      Home
                    </button>
                    <button
                      onClick={() => handleNavigate("services")}
                      className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600"
                    >
                      Services
                    </button>
                    <button
                      onClick={() => handleNavigate("login")}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Login
                    </button>
                  </div>
                </div>
              </div>
            </nav>

            {/* Hero Section */}
            <section className="py-20 text-center">
              <div className="max-w-4xl mx-auto px-4">
                <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
                  Welcome to Seva Sindhu
                </h1>
                <p className="text-xl md:text-2xl text-gray-600 mb-8">
                  Your gateway to government services in India
                </p>
                <button
                  onClick={() => handleNavigate("services")}
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700"
                >
                  Explore Services
                </button>
              </div>
            </section>

            {/* Services Grid */}
            <section className="py-16 bg-white">
              <div className="max-w-7xl mx-auto px-4">
                <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
                  Popular Government Services
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {[
                    { icon: "🛂", name: "Passport Services", desc: "Apply for passport and related services" },
                    { icon: "🆔", name: "Aadhaar Services", desc: "Update Aadhaar details" },
                    { icon: "💳", name: "PAN Card", desc: "Apply for PAN card" },
                    { icon: "🏛️", name: "EPFO Services", desc: "Manage EPF account" },
                    { icon: "🚗", name: "Driving License", desc: "Apply for driving license" },
                    { icon: "🎓", name: "Education", desc: "Educational services" }
                  ].map((service, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-6 hover:shadow-lg transition-shadow">
                      <div className="text-4xl mb-4">{service.icon}</div>
                      <h3 className="text-xl font-semibold mb-3 text-gray-900">{service.name}</h3>
                      <p className="text-gray-600">{service.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-800 text-white py-12">
              <div className="max-w-7xl mx-auto px-4 text-center">
                <p>&copy; 2024 Seva Sindhu - Government of India. All rights reserved.</p>
              </div>
            </footer>
          </div>
        );
      case "services":
        return (
          <div className="min-h-screen bg-gray-50">
            <nav className="bg-white shadow-lg">
              <div className="max-w-7xl mx-auto px-4">
                <div className="flex justify-between items-center h-16">
                  <div className="flex items-center">
                    <h1 className="text-2xl font-bold text-blue-600">🏛️ Seva Sindhu</h1>
                  </div>
                  <div className="flex space-x-4">
                    <button
                      onClick={() => handleNavigate("home")}
                      className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600"
                    >
                      Home
                    </button>
                    <button
                      onClick={() => handleNavigate("services")}
                      className="px-3 py-2 rounded-md text-sm font-medium bg-blue-100 text-blue-700"
                    >
                      Services
                    </button>
                    <button
                      onClick={() => handleNavigate("login")}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Login
                    </button>
                  </div>
                </div>
              </div>
            </nav>
            <div className="py-12">
              <div className="max-w-7xl mx-auto px-4">
                <h1 className="text-3xl font-bold text-center mb-12">All Services</h1>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {[
                    { icon: "🛂", name: "Passport Services" },
                    { icon: "🆔", name: "Aadhaar Services" },
                    { icon: "💳", name: "PAN Card" },
                    { icon: "🏛️", name: "EPFO Services" },
                    { icon: "🚗", name: "Driving License" },
                    { icon: "🎓", name: "Education" }
                  ].map((service, index) => (
                    <div key={index} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg">
                      <div className="text-3xl mb-3">{service.icon}</div>
                      <h3 className="text-lg font-semibold">{service.name}</h3>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );
      case "login":
        return (
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-8">
              <div className="text-center mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">🏛️ Seva Sindhu</h1>
                <p className="text-gray-600">Login to your account</p>
              </div>
              
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                  <input
                    type="password"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                  onClick={(e) => {
                    e.preventDefault();
                    alert('Login successful!');
                    handleNavigate('home');
                  }}
                >
                  Login
                </button>
              </form>
              
              <div className="mt-6 text-center">
                <p className="text-gray-600">
                  Don't have an account? <button className="text-blue-600 hover:text-blue-700 font-medium">Sign up</button>
                </p>
              </div>
            </div>
          </div>
        );
      default:
        return <div>Page not found</div>;
    }
  };

  return (
    <div>
        {renderPage()}
    </div>
  );
}

export default App;