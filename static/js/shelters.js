$(document).ready(function() {
  const cancelBtn = document.getElementById("cancelReservationButton");
  const makeBtn = document.getElementById("makeReservationButton");
  const makeAmount = document.getElementById("makeReservationAmount");

  const swapReserveContainer = () => {
    $("#cancelContainer").toggle();
    $("#reserveContainer").toggle();
  };

  const changeMessage = (message) => {

    $("#feedbackContainer").html(message);
  }

  const updateCapacity = (delta) => {
    $("#capacity").html(parseInt($("#capacity").text()) + delta);
  }

  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      const shelterId = window.location.href.split("/").slice(-1);
      $.ajax({
	url: "/cancel/" + shelterId,
	type: "POST",
	success: function(data) {
	  data = JSON.parse(data);
	  if (data["status"] == "ok") {
	    swapReserveContainer();
	    updateCapacity(data["delta"]);
	  }
	  changeMessage(data["msg"]);
	},
	error: function(data) {
	  console.log("network error");
	}
      });
    });
  }

  if (makeBtn) {
    makeBtn.addEventListener("click", () => {
      const shelterId = window.location.href.split("/").slice(-1);
      $.ajax({
	url: "/reserve/" + shelterId,
	data: {
	  "amount": makeAmount.value
	},
	type: "POST",
	success: function(data) {
	  data = JSON.parse(data);
	  if (data["status"] == "ok") {
	    swapReserveContainer();
	    updateCapacity(data["delta"]);
	  }
	  changeMessage(data["msg"]);
	},
	error: function(data) {
	  console.log("network error");
	}
      });
    });
  }
});
