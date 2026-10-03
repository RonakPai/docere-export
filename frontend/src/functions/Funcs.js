const baseURL =
  window.location.hostname === "localhost"
    ? "http://localhost:5000"
    : "http://backend-balancer-1817433525.us-west-1.elb.amazonaws.com:5000";

const getCookie = (name) =>
  document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`))
    ?.split("=")[1] || null;

export { baseURL, getCookie };
