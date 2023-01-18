function getTokenFromCookieOrLocalStorage() {
    // Try to get the JWT token from a cookie
    let token = getCookie("jwt_token");

    // If the token is not found in the cookie, try to get it from local storage
    if (!token) {
        token = localStorage.getItem("jwt_token");
    }

    return token;
}

function getCookie(name) {
    // Split the cookies string into an array of individual cookies
    const cookies = document.cookie.split(";");

    // Find the cookie with the specified name
    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.split("=");
        if (cookieName.trim() === name) {
            return cookieValue;
        }
    }

    // If no cookie with the specified name is found, return null
    return null;
}

function setTokenInCookie(token) {
    document.cookie = `token=${token}; max-age=72000`;
}

function getTokenFromCookie() {
    const cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
        const [name, value] = cookie.split("=");
        if (name === "jwt_token") {
            return value;
        }
    }
    return null;
}
