document.getElementById('addCourseButton').addEventListener('click', function () {
    document.getElementById('courseModal').style.display = 'flex';
    
});

document.getElementById('closeModal').addEventListener('click', function () {
    document.getElementById('courseModal').style.display = 'none';
});

document.getElementById('addCourseForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const courseId = document.getElementById('availableCourses').value;
    let courses = JSON.parse(localStorage.getItem('courses')) || [];

    if (!courses.includes(courseId)) {
        courses.push(courseId);
        localStorage.setItem('courses', JSON.stringify(courses));
        createCourseCard(courseId);
    }
    document.getElementById('courseModal').style.display = 'none';
});

document.addEventListener('DOMContentLoaded', function () {
// Ensures modal is hidden by default
document.getElementById('courseModal').style.display = 'none'; 

const savedCourses = JSON.parse(localStorage.getItem('courses')) || [];
savedCourses.forEach(courseName => {
createCourseCard(courseName);
});
});


const courseData = {
    "apcalc": "AP Calculus BC",
    "apphysicsc_mechanics": "AP Physics C: Mechanics",
    "apphysicsc_electricity": "AP Physics C: Electricity and Magnetism",
    "apush": "AP U.S. History"
};

function createCourseCard(courseId) {
    const courseBox = document.createElement('div');
    courseBox.classList.add('course-card');
    courseBox.setAttribute('data-course-id', courseId);

    courseBox.innerHTML = `
<div class="course-icon">
    <div class="course-text">${getCourseName(courseId)}</div>
</div>
<button class="delete-icon" title="Delete Course">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20px" height="20px">
        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
    </svg>
</button>
`;

    document.getElementById('coursesContainer').appendChild(courseBox);

    let isDeleting = false;

    courseBox.addEventListener('click', function () {
        if (!isDeleting) {
            window.location.href = `/studyguide?course=${courseId}`;
        } else {
            removeCourse(courseId, courseBox); 
        }
    });

    courseBox.querySelector('.delete-icon').addEventListener('click', function (e) {
        e.stopPropagation(); 

        if (!isDeleting) {
            isDeleting = true;
            courseBox.querySelector('.course-text').textContent = "Delete Course?";
            this.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20px" height="20px">
            <path d="M19 13H5v-2h14v2z"/>
        </svg>
    `; 
        } else {
            isDeleting = false;
            courseBox.querySelector('.course-text').textContent = getCourseName(courseId);
            this.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20px" height="20px">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
        </svg>
    `; 
        }
    });
}

function getCourseName(courseId) {
    const courses = {
        apcalc: 'AP Calculus BC',
        apush: 'AP U.S. History',
        apphysicsc_mechanics: 'AP Physics C: Mechanics',
        apphysicsc_electricity: 'AP Physics C: Electricity and Magnetism'
    };
    return courses[courseId] || courseId;
}



function removeCourse(courseId, courseBox) {
    let courses = JSON.parse(localStorage.getItem('courses')) || [];
    courses = courses.filter(course => course !== courseId);
    localStorage.setItem('courses', JSON.stringify(courses));
    courseBox.remove();
}
