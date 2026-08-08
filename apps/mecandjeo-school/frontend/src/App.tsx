import AppRoutes from "./routes/AppRoutes";

export default function App() {
  return <AppRoutes />;
}








// /**
//  * Temporary API Foundation Test
//  *
//  * This component verifies:
//  * - React rendering
//  * - Axios configuration
//  * - Environment variables
//  */

// import api from "./services/api";

// function App() {
//   const testApiConnection = async () => {
//     try {
//       /**
//        * We expect this endpoint
//        * to exist in our FastAPI backend.
//        */
//       const response = await api.get("/health");

//       console.log("Backend Response:", response.data);

//       alert("API Connection Successful");
//     } catch (error) {
//       console.error("API Connection Failed:", error);

//       alert("API Connection Failed");
//     }
//   };

//   return (
//     <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-gray-100">
//       <h1 className="text-3xl font-bold text-blue-600">
//         API Foundation Test
//       </h1>

//       <button
//         onClick={testApiConnection}
//         className="px-6 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700"
//       >
//         Test Backend Connection
//       </button>
//     </div>
//   );
// }

// export default App;
