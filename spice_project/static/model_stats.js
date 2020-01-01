var table = document.getElementById("results-table");

function retrieveModelStats() {
    return $.ajax({
        url: "/retrieve_model_stats",
        type: "GET",
        headers: {
            Accept: "application/json"
        },
        success: function(data) {
            data = JSON.parse(data);

            var mean_sd_model_time = document.getElementById("mean-sd-model-time"),
                mean_sd_result_time = document.getElementById("mean-sd-result-time"),
                mean_sd_acc = document.getElementById("mean-sd-acc"),
                pca_model_time = document.getElementById("pca-model-time"),
                pca_result_time = document.getElementById("pca-result-time"),
                pca_acc = document.getElementById("pca-acc"),
                lda_model_time = document.getElementById("lda-model-time"),
                lda_result_time = document.getElementById("lda-result-time"),
                lda_acc = document.getElementById("lda-acc");

            mean_sd_model_time.innerHTML += data["mean_and_sd"]["model_time"] + "s";
            mean_sd_result_time.innerHTML += data["mean_and_sd"]["pred_time"] + "s";
            mean_sd_acc.innerHTML += data["mean_and_sd"]["acc"] + "%";
            pca_model_time.innerHTML += data["pca"]["model_time"] + "s";
            pca_result_time.innerHTML += data["pca"]["pred_time"] + "s";
            pca_acc.innerHTML += data["pca"]["acc"] + "%";
            lda_model_time.innerHTML += data["lda"]["model_time"] + "s";
            lda_result_time.innerHTML += data["lda"]["pred_time"] + "s";
            lda_acc.innerHTML += data["lda"]["acc"] + "%";
        }
    })
}

retrieveModelStats();
