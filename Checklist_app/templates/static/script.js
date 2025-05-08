document.addEventListener('DOMContentLoaded', function () {
  const checklistButtons = document.querySelectorAll('.btn-checklist');

  checklistButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
          alert("Checklist diklik untuk ID: " + btn.dataset.alatId);
      });
  });
});
