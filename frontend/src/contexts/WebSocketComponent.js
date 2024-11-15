import jwt_decode from "jwt-decode";
import { useEffect, useState } from "react";

function isTokenExpired(token) {
    const decoded = jwt_decode(token);
    const currentTime = Date.now() / 1000;  // in seconds
    return decoded.exp < currentTime;
}

const MyWebSocketComponent = () => {
    const [socket, setSocket] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("access_token");

        // Check if the token is expired
        if (token && !isTokenExpired(token)) {
            // Establish WebSocket connection with the valid token
            const ws = new WebSocket(`ws://localhost:8000/ws/albums/?token=${token}`);

            ws.onopen = () => {
                console.log("WebSocket connected");
            };

            ws.onmessage = (event) => {
                console.log("Received:", event.data);
            };

            ws.onclose = () => {
                console.log("WebSocket connection closed");
            };

            ws.onerror = (error) => {
                console.error("WebSocket error", error);
            };

            setSocket(ws);
        } else {
            setError("Token expired. Please login again.");
            // Optionally, you can refresh the token or redirect to login
            console.log("Token has expired, redirecting to login...");
            // Redirect to login page, or handle token refresh logic
        }

        return () => {
            if (socket) {
                socket.close();
            }
        };
    }, []);

    return (
        <div>
            {error && <p>{error}</p>}
            {/* Your WebSocket interaction goes here */}
        </div>
    );
};

export default MyWebSocketComponent;
