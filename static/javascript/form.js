document.querySelectorAll(".radio_bool_COVID").forEach((item) => {
  item.addEventListener("click", (event) => {
    if (document.getElementById("inputFemale").checked) {
      jQuery(function ($) {
        $(".female").slideToggle("slow");
      });
    }
    if (document.getElementById("inputCOVIDFormFillGuy").checked) {
      jQuery(function ($) {
        $(".meOrRecovered").slideToggle("slow");
        $(".symptomsFormHeader").slideToggle("slow");
        $(".symptoms").slideToggle("slow");
      });
    }
    if (document.getElementById("inputCaregiver").checked || document.getElementById("inputNOTA").checked) {
      jQuery(function ($) {
        $(".caregiverOrNOTA").slideToggle("slow");
        $(".symptomsCaregiverHeader").slideToggle("slow");
        $(".symptoms").slideToggle("slow");
      });
    }
    if (document.getElementById("inputCaregiver").checked) {
      jQuery(function ($) {
        $(".caregiverOnly").slideToggle("slow");
      });
    }
    if (document.getElementById("inputRecovered").checked) {
      jQuery(function ($) {
        $(".meOrRecovered").slideToggle("slow");
        $(".symptomsFormHeader").slideToggle("slow");
        $(".symptoms").slideToggle("slow");
        $(".recoveredOnly").slideToggle("slow");
      });
    }
  });
});

var checkedRadio;
function ClearRd(o) {
  if (checkedRadio == o) {
    o.checked = false;
    o.value = "False";
    checkedRadio = null;
  } else {
    checkedRadio = o;
  }
}

var checkedRadioDiseases;
function ClearRdDiseases(o) {
  if (checkedRadioDiseases == o) {
    // o.checked = false;
    o.value = "False";
    checkedRadioDiseases = null;
  } else {
    checkedRadioDiseases = o;
  }
}