// import React, { useEffect, useState } from "react";
// import axios from "axios";
// import { motion } from "framer-motion";
// import "./App.css";


// const API_URL = "http://127.0.0.1:5000"; // Flask backend URL

// export default function App() {
//   const [veggies, setVeggies] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [cart, setCart] = useState([]);
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const [token, setToken] = useState("");
//   const [message, setMessage] = useState("");

//   useEffect(() => {
//     fetchVeggies();
//   }, []);

//   async function fetchVeggies() {
//     setLoading(true);
//     try {
//       const res = await axios.get(`${API_URL}/vegetables`);
//       setVeggies(res.data);
//     } catch (err) {
//       console.error(err);
//     }
//     setLoading(false);
//   }

//   function addToCart(veg) {
//     setCart([...cart, { ...veg, quantity: 1 }]);
//   }

//   async function register() {
//     try {
//       await axios.post(`${API_URL}/auth/register`, { username, password });
//       setMessage("✅ Registered! You can log in now.");
//     } catch (err) {
//       setMessage("❌ " + err.response?.data?.msg || "Error");
//     }
//   }

//   async function login() {
//     try {
//       const res = await axios.post(`${API_URL}/auth/login`, { username, password });
//       setToken(res.data.access_token);
//       setMessage("✅ Logged in!");
//     } catch (err) {
//       setMessage("❌ " + err.response?.data?.msg || "Error");
//     }
//   }

//   async function placeOrder() {
//     if (!token) {
//       setMessage("❌ Please login first!");
//       return;
//     }
//     try {
//       const items = cart.map(c => ({ vegetable_id: c.id, quantity: c.quantity }));
//       await axios.post(`${API_URL}/orders`, { items }, {
//         headers: { Authorization: `Bearer ${token}` }
//       });
//       setMessage("✅ Order placed successfully!");
//       setCart([]);
//       fetchVeggies();
//     } catch (err) {
//       setMessage("❌ " + err.response?.data?.msg || "Error");
//     }
//   }

//   return (
//     <div className="bg-green-50 min-h-screen p-6">
//       <motion.h1 
//         initial={{ opacity: 0, y: -20 }} 
//         animate={{ opacity: 1, y: 0 }}
//         transition={{ duration: 0.5 }}
//         className="text-4xl font-bold text-green-700 mb-4 text-center"
//       >
//         🌱 Veggie Vendor
//       </motion.h1>

//       {/* Auth Section */}
//       <div className="flex gap-2 mb-6 justify-center">
//         <input
//           type="text"
//           placeholder="Username"
//           className="border rounded p-2"
//           onChange={(e) => setUsername(e.target.value)}
//         />
//         <input
//           type="password"
//           placeholder="Password"
//           className="border rounded p-2"
//           onChange={(e) => setPassword(e.target.value)}
//         />
//         <button onClick={register} className="bg-green-500 text-white px-3 py-2 rounded hover:bg-green-600 transition">Register</button>
//         <button onClick={login} className="bg-yellow-500 text-white px-3 py-2 rounded hover:bg-yellow-600 transition">Login</button>
//       </div>

//       {message && <p className="text-center mb-4">{message}</p>}

//       {/* Veggie List */}
//       {loading ? (
//         <p className="text-center text-gray-500">Loading veggies...</p>
//       ) : (
//         <motion.div 
//           layout
//           className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6"
//         >
//           {veggies.map((veg) => (
//             <motion.div 
//               key={veg.id} 
//               initial={{ opacity: 0, scale: 0.9 }} 
//               animate={{ opacity: 1, scale: 1 }}
//               whileHover={{ scale: 1.05 }}
//               className="bg-white shadow-lg rounded-lg p-4"
//             >
//               <h2 className="text-xl font-semibold text-green-700">{veg.name}</h2>
//               <p className="text-gray-500">{veg.description}</p>
//               <p className="text-lg font-bold">₹{veg.price}</p>
//               <p className="text-sm text-gray-400">Stock: {veg.stock}</p>
//               <button 
//                 onClick={() => addToCart(veg)} 
//                 className="mt-2 w-full bg-green-500 text-white py-2 rounded hover:bg-green-600 transition"
//               >
//                 Add to Cart
//               </button>
//             </motion.div>
//           ))}
//         </motion.div>
//       )}

//       {/* Cart Section */}
//       <motion.div 
//         initial={{ y: 100, opacity: 0 }} 
//         animate={{ y: 0, opacity: 1 }}
//         className="mt-6 bg-white shadow-lg rounded-lg p-4"
//       >
//         <h2 className="text-2xl font-bold mb-4">🛒 Cart</h2>
//         {cart.length === 0 ? <p>No items yet.</p> : (
//           <>
//             {cart.map((item, i) => (
//               <div key={i} className="flex justify-between border-b py-2">
//                 <span>{item.name} × {item.quantity}</span>
//                 <span>₹{item.price * item.quantity}</span>
//               </div>
//             ))}
//             <button 
//               onClick={placeOrder} 
//               className="mt-4 w-full bg-yellow-500 text-white py-2 rounded hover:bg-yellow-600 transition"
//             >
//               Place Order
//             </button>
//           </>
//         )}
//       </motion.div>
//     </div>
//   );
// }
// import React from "react";
// import "./App.css";

// function App() {
//   const veggies = [
//     { name: "Tomato", price: 30, img: "https://i.postimg.cc/4ybXk6ss/tomato.jpg" },
//     { name: "Potato", price: 25, img: "https://i.postimg.cc/yNkbt8YR/potato.jpg" },
//     { name: "Carrot", price: 40, img: "https://i.postimg.cc/6qPcsn3w/carrot.jpg" },
//     { name: "Broccoli", price: 60, img: "https://i.postimg.cc/8PdYjFJc/broccoli.jpg" },
//   ];

//   const handleBuy = (vegName) => {
//     alert(`You have bought ${vegName}!`);
//   };

//   return (
//     <div className="app">
//       <header>
//         <h1>Fresh Veggie Vendor 🥦</h1>
//         <p>Fresh from the farm to your plate</p>
//       </header>

//       <div className="veggie-container">
//         {veggies.map((veg, index) => (
//           <div className="veggie-card" key={index}>
//             <img src={veg.img} alt={veg.name} />
//             <h2>{veg.name}</h2>
//             <p>₹{veg.price} / kg</p>
//             <button onClick={() => handleBuy(veg.name)}>Buy Now</button>
//           </div>
//         ))}
//       </div>

//       <footer>
//         <p>© 2025 Fresh Veggie Vendor | Eat Healthy 🌱</p>
//       </footer>
//     </div>
//   );
// }

// export default App;

// import React, { useState } from "react";
// import "./App.css";

// function App() {
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");

//   const handleLogin = (e) => {
//     e.preventDefault();
//     if (username && password) {
//       alert(`Welcome, ${username}!`);
//     } else {
//       alert("Please fill in all fields.");
//     }
//   };

//   return (
//     <div className="login-container">
//       <div className="login-card">
//         <h1>🥦 Veggie Vendor Login</h1>
//         <form onSubmit={handleLogin}>
//           <input
//             type="text"
//             placeholder="Enter Username"
//             value={username}
//             onChange={(e) => setUsername(e.target.value)}
//           />
//           <input
//             type="password"
//             placeholder="Enter Password"
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//           />
//           <button type="submit">Login</button>
//         </form>
//         <p className="note">Fresh veggies await you 🌱</p>
//       </div>
//     </div>
//   );
// }

// export default App;

import React, { useState } from "react";
import "./App.css";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    if (email && password) {
      alert(`Welcome, ${email}!`);
    } else {
      alert("Please fill in both fields.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1><b><i><strong>KLOUDCART</strong></i></b></h1>
        <h2 className="title">🥦 Veggie Vendor</h2>
        <p className="subtitle">Freshness at your doorstep 🌱</p>
        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label>Email:</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="input-group">
            <label>Password:</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button className="login-btn" type="submit">
            Login
          </button>
        </form>
        <p className="register-text">
          Don't have an account? <a href="#">Register Now</a>
        </p>
      </div>
    </div>
  );
}

export default App;
