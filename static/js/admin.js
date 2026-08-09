/**
 * Faculty & Admin Dashboard Interactions
 * =====================================
 * Live student filtering, attempt history modal viewer, and question controls.
 */

document.addEventListener("DOMContentLoaded", function () {
  // Student Search Filter
  const studentSearchInput = document.getElementById("student-search-input");
  const studentTableRows = document.querySelectorAll(".student-table-row");

  if (studentSearchInput && studentTableRows.length > 0) {
    studentSearchInput.addEventListener("input", function () {
      const query = this.value.toLowerCase().trim();

      studentTableRows.forEach((row) => {
        const text = row.innerText.toLowerCase();
        if (text.includes(query)) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  }

  // View Student History Modal
  const viewHistoryButtons = document.querySelectorAll(".btn-view-history");
  const historyModal = document.getElementById("student-history-modal");
  const modalContentBody = document.getElementById("history-modal-body");
  const modalStudentName = document.getElementById("modal-student-name");

  viewHistoryButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const studentId = this.getAttribute("data-student-id");
      if (!historyModal || !modalContentBody) return;

      modalContentBody.innerHTML = `
        <div style="text-align: center; padding: 30px;">
          <p>⏳ Loading student records...</p>
        </div>
      `;
      historyModal.style.display = "flex";

      fetch(`/admin/students/${studentId}/history`)
        .then((res) => res.json())
        .then((data) => {
          if (modalStudentName) {
            modalStudentName.innerText = `${data.student.name} (${data.student.roll_no})`;
          }

          if (data.attempts.length === 0) {
            modalContentBody.innerHTML = `
              <div style="text-align: center; padding: 24px; color: #94a3b8;">
                <p>No examination attempts recorded yet for this student.</p>
              </div>
            `;
            return;
          }

          let tableHtml = `
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Exam Title</th>
                    <th>Score</th>
                    <th>Percentage</th>
                    <th>Grade</th>
                    <th>Status</th>
                    <th>Certificate ID</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
          `;

          data.attempts.forEach((att) => {
            const statusBadge = att.is_passed
              ? `<span class="badge badge-passed">Passed</span>`
              : `<span class="badge badge-failed">Failed</span>`;

            tableHtml += `
              <tr>
                <td><strong>${att.exam_title}</strong></td>
                <td>${att.score}</td>
                <td>${att.percentage}</td>
                <td><span class="badge badge-medium">${att.grade}</span></td>
                <td>${statusBadge}</td>
                <td><code style="color: #818cf8;">${att.certificate_id}</code></td>
                <td>${att.date}</td>
              </tr>
            `;
          });

          tableHtml += `</tbody></table></div>`;
          modalContentBody.innerHTML = tableHtml;
        })
        .catch((err) => {
          modalContentBody.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #ef4444;">
              <p>Failed to load student history. Please try again.</p>
            </div>
          `;
        });
    });
  });

  // Modal Close buttons
  const closeModalBtns = document.querySelectorAll(".btn-close-modal");
  closeModalBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      if (historyModal) historyModal.style.display = "none";
    });
  });

  window.addEventListener("click", function (e) {
    if (e.target === historyModal) {
      historyModal.style.display = "none";
    }
  });
});
