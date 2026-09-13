document.addEventListener("DOMContentLoaded", () => {
  const c = window.CHARTS || {};
  const common = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { usePointStyle: true, boxWidth: 7, font: { size: 10 } } } },
    scales: { x: { grid: { display: false }, ticks: { font: { size: 9 } } },
              y: { grid: { color: "#edf0f4" }, ticks: { font: { size: 9 } } } }
  };

  if (c.churn) new Chart(document.getElementById("churnChart"), {
    type:"doughnut",
    data:{labels:c.churn.labels,datasets:[{data:c.churn.values,backgroundColor:["#ff6b1a","#dfe4eb"],borderWidth:0}]},
    options:{responsive:true,maintainAspectRatio:false,cutout:"72%",plugins:{legend:{position:"bottom",labels:{usePointStyle:true,boxWidth:8,font:{size:10}}}}}
  });

  if (c.contract) new Chart(document.getElementById("contractChart"), {
    type:"bar",
    data:{labels:c.contract.labels,datasets:[
      {label:"Churn",data:c.contract.yes,backgroundColor:"#ff6b1a",borderRadius:5},
      {label:"Retained",data:c.contract.no,backgroundColor:"#dfe4eb",borderRadius:5}
    ]},options:common
  });

  function histogram(id, data) {
    if (!data) return;
    new Chart(document.getElementById(id), {
      type:"bar",
      data:{labels:data.labels,datasets:[{data:data.values,backgroundColor:"#ff9550",borderRadius:5}]},
      options:{...common,plugins:{legend:{display:false}}}
    });
  }
  histogram("tenureChart",c.tenure);
  histogram("chargesChart",c.charges);

  if (c.scatter) new Chart(document.getElementById("scatterChart"), {
    type:"scatter",
    data:{datasets:[{label:"Customers",data:c.scatter.x.map((x,i)=>({x:x,y:c.scatter.y[i]})),backgroundColor:"#ff6b1a",pointRadius:3}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:"Tenure (months)"},grid:{display:false}},y:{title:{display:true,text:"Monthly Charges"},grid:{color:"#edf0f4"}}}}
  });
});
