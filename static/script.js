let dateInput = document.getElementById("dateInput");
let logsList = document.getElementById("logsList");
let dailyTotal = document.getElementById("dailyTotal");

dateInput.value = new Date().toISOString().split("T")[0];

function fetchLogs() {
  let d = dateInput.value;
  fetch(`/api/logs/${d}`)
    .then(res => res.json())
    .then(data => {
      logsList.innerHTML = "";
      data.forEach(item => {
        let li = document.createElement("li");
        if (item.grams !== undefined) {
          li.textContent = `${item.meal} - ${item.food} (${item.grams}g)`;
        } else {
          li.textContent = `${item.meal} - ${item.food} (${item.kcal} kcal)`;
        }
        logsList.appendChild(li);
      });
    });
}

function fetchTotal() {
  let d = dateInput.value;
  fetch(`/api/daily_total/${d}`)
    .then(res => res.json())
    .then(data => {
      dailyTotal.textContent = JSON.stringify(data, null, 2);
    });
}

function addFood() {
  let d = dateInput.value;
  let text = document.getElementById("foodInput").value;
  let parts = text.split(" ");
  let name = parts[0];
  let grams = parseInt(parts[1]);

  let item = {
    meal: "午餐",
    food: name,
    grams: grams
  };

  fetch("/api/add_food", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date: d, item: item })
  }).then(() => {
    fetchLogs();
    fetchTotal();
  });
}




dateInput.onchange = () => {
  fetchLogs();
  fetchTotal();
};

fetchLogs();
fetchTotal();
