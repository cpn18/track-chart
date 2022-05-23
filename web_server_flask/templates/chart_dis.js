// UNH Capstone 2022 Project
//
// Ben Grimes, Jeff Fernandes, Max Hennessey, Liqi Li

function info() {
    var url_s = window.location.href;
    var url = new URL(url_s);
    var location = url.searchParams.get("location");
    submitOK = "true";
}
