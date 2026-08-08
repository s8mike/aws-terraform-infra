/**
 * JWT Authentication Verification Test
 *
 * Purpose:
 * Tests that Axios automatically attaches
 * the JWT token to protected API requests.
 *
 * This file exists separately from App.tsx
 * because testing logic should not be mixed
 * with application startup code.
 */

import api from "../../services/api";


function JWTTest() {


  // Test protected endpoint using stored JWT
  const testJWT = async () => {

    try {

      // Axios interceptor adds JWT automatically
      const response = await api.get("/api/me");


      console.log(
        "Authenticated User:",
        response.data
      );


      alert(
        "JWT Authentication Successful"
      );


    } catch (error) {


      console.error(
        "JWT Authentication Failed:",
        error
      );


      alert(
        "JWT Authentication Failed"
      );
    }
  };


  return (

    <div
      className="
        min-h-screen
        flex
        flex-col
        items-center
        justify-center
        gap-4
        bg-gray-100
      "
    >

      <h1
        className="
          text-3xl
          font-bold
          text-blue-600
        "
      >
        JWT Verification Test
      </h1>


      <button
        onClick={testJWT}
        className="
          px-6
          py-3
          rounded-lg
          bg-blue-600
          text-white
          hover:bg-blue-700
        "
      >
        Test Protected API
      </button>

    </div>

  );
}


export default JWTTest;