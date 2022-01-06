function changeRule() {
    event.preventDefault()
    min_age = document.getElementById('min_age').value
    max_age = document.getElementById('max_age').value
    max_size = document.getElementById('max_size').value

    fetch("/api/change-rule", {
        method: 'PUT',
        body: JSON.stringify({
            'min_age': min_age,
            'max_age': max_age,
            'max_size': max_size
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        a = document.getElementById('alert')

        if(data.status == 200) {
            a.style.display = "block"
            a.className = "alert alert-success"
            a.innerText = "Thay đổi thành công"
        }
        else {
           a.style.display = "block"
           a.className = "alert alert-danger"
           a.innerText = "Có dữ liệu vi phạm ràng buộc"
        }

        $(a).fadeOut(3000)
    }).catch(function(err) {
        console.info(err)
    })
}

function loadChart(ctx, labels, data, type, colors, borderColors, title) {
        const myChart = new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: data,
                    backgroundColor: colors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        })
}

function updateMarks(subject_id, student_id, year) {
    event.preventDefault()
    mark15_1_obj = document.getElementsByClassName('mark15_1')
    mark45_1_obj = document.getElementsByClassName('mark45_1')
    mark15_2_obj = document.getElementsByClassName('mark15_2')
    mark45_2_obj = document.getElementsByClassName('mark45_2')
    final_mark1 = document.getElementById('final_mark1').value
    final_mark2 = document.getElementById('final_mark2').value
    mark15_1 = []
    mark45_1 = []
    mark15_2 = []
    mark45_2 = []

    for(let i = 0; i < 5; i++) {
        mark15_1[i] = mark15_1_obj[i].value
        mark15_2[i] = mark15_2_obj[i].value
    }

    for(let i = 0; i < 3; i++) {
        mark45_1[i] = mark45_1_obj[i].value
        mark45_2[i] = mark45_2_obj[i].value
    }

    fetch("/api/update-mark", {
        method: 'PUT',
        body: JSON.stringify({
            'subject_id':subject_id,
            'student_id':student_id,
            'year': year,
            'mark15_1': mark15_1,
            'mark45_1': mark45_1,
            'mark15_2': mark15_2,
            'mark45_2': mark45_2,
            'final_mark1': final_mark1,
            'final_mark2': final_mark2
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        a = document.getElementById('alert')

        if(data.status == 200) {
            a.style.display = "block"
            a.className = "alert alert-success"
            a.innerText = "Lưu thành công"
        }
        else {
           a.style.display = "block"
           a.className = "alert alert-danger"
           a.innerText = "Lưu thất bại"
           console.info(data.err_msg)
        }

        $(a).fadeOut(3000)
    }).catch(function(err) {
        console.info(err)
    })
}

function loadMarks(course_id) {
     clear_marks()
     fetch("/api/load-marks", {
        method: 'POST',
        body: JSON.stringify({
            'course_id': course_id,
            'semester': document.getElementById('semester').value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {

        if(data.status == 200) {
            marks = data.marks
            console.info(marks)

            for(let i = 0; i < marks.length; i++) {
                marks15 = document.getElementsByClassName('mark15_' + marks[i].student_id)
                marks45 = document.getElementsByClassName('mark45_' + marks[i].student_id)

                for(let j = 0; j < 5; j++) {
                    marks15[j].innerText = marks[i].mark15[j]
                }
                for(let j = 0; j < 3; j++) {
                    marks45[j].innerText = marks[i].mark45[j]
                }
                document.getElementById('final_mark_' + marks[i].student_id).innerText = marks[i].final_mark
                document.getElementById('avg_mark_' + marks[i].student_id).innerText = marks[i].avg_mark
            }


        }
        else {
           console.info("that bai")
        }

    }).catch(function(err) {
        console.info(err)
    })
}

function clear_marks() {
    marks = document.getElementsByClassName('marks')
    for (let i = 0; i < marks.length; i++) {
         marks[i].innerText = ''
    }
}
