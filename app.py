import streamlit as st
from database_setup import DatabaseManager

class UdemyClone:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None

    def login_page(self):
        st.title('Login to Udemy Clone')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            user = self.db.authenticate_user(username, password)
            if user:
                st.session_state['username'] = username
                st.session_state['user_id'] = user[0]
                st.session_state['user_role'] = self.db.get_user_role(username)
                st.success('Login Successful!')
                st.rerun()
            else:
                st.error('Invalid credentials')

    def registration_page(self):
        st.title('Register for Udemy Clone')
        new_username = st.text_input('Choose Username')
        new_password = st.text_input('Choose Password', type='password')
        email = st.text_input('Email Address')
        role = st.selectbox('Register As', ['student', 'instructor'])

        if st.button('Register'):
            if self.db.register_user(new_username, new_password, email, role):
                st.success('Registration Successful! Please Login.')
            else:
                st.error('Username or Email already exists')

    def admin_dashboard(self):
        st.title(f'Admin Dashboard - Welcome {st.session_state["username"]}')
        action = st.selectbox('Admin Actions', [
            'Manage Users',
            'View All Courses',
            'System Statistics'
        ])

        if action == 'Manage Users':
            self.manage_users()
        elif action == 'View All Courses':
            self.view_all_courses()
        elif action == 'System Statistics':
            self.system_statistics()

    def student_dashboard(self):
        st.title(f'Student Dashboard - Welcome {st.session_state["username"]}')
        action = st.selectbox('Student Actions', [
            'Browse Courses',
            'My Enrollments',
            'Profile'
        ])

        if action == 'Browse Courses':
            self.browse_courses()
        elif action == 'My Enrollments':
            self.my_enrollments()
        elif action == 'Profile':
            self.profile()

    def instructor_dashboard(self):
        st.title(f'Instructor Dashboard - Welcome {st.session_state["username"]}')
        action = st.selectbox('Instructor Actions', [
            'Create Course',
            'My Courses',
            'Course Analytics'
        ])

        if action == 'Create Course':
            self.create_course()
        elif action == 'My Courses':
            self.my_courses()
        elif action == 'Course Analytics':
            self.course_analytics()

    def create_course(self):
        st.subheader('Create a New Course')
        title = st.text_input('Course Title')
        description = st.text_area('Course Description')
        price = st.number_input('Course Price', min_value=0.0, step=0.5)

        if st.button('Create Course'):
            if self.db.create_course(title, description, st.session_state['user_id'], price):
                st.success('Course created successfully!')
            else:
                st.error('Failed to create course')

    def my_courses(self):
        st.subheader('My Courses')
        courses = self.db.get_courses_by_instructor_id(st.session_state['user_id'])

        if courses:
            for course in courses:
                st.write(f"**{course[1]}**")  # Course Title
                st.write(f"Description: {course[2]}")
                st.write(f"Price: ${course[4]}")
                enrolled_count = self.db.get_enrolled_students_count(course[0])
                st.write(f"Enrolled Students: {enrolled_count}")
                st.write("---")
        else:
            st.info('You have not created any courses yet.')

    def course_analytics(self):
        st.subheader('Course Analytics')
        st.write('Coming soon...')

    def browse_courses(self):
        st.subheader('Available Courses')
        courses = self.db.get_all_courses()
        
        if courses:
            for course in courses:
                st.write(f"**{course[1]}**")  # Course Title
                st.write(f"Description: {course[2]}")
                st.write(f"Price: ${course[4]}")
                instructor_name = self.db.get_instructor_name(course[3])
                st.write(f"Instructor: {instructor_name}")
                
                if st.button(f'Enroll in {course[1]}', key=course[0]):
                    if self.db.enroll_course(st.session_state['user_id'], course[0]):
                        st.success(f'You have successfully enrolled in {course[1]}!')
                    else:
                        st.error('You are already enrolled in this course or an error occurred.')
                st.write("---")
        else:
            st.info('No courses available at the moment.')

    def my_enrollments(self):
        st.subheader('My Enrolled Courses')
        courses = self.db.get_enrolled_courses(st.session_state['user_id'])
        
        if courses:
            for course in courses:
                st.write(f"**{course[1]}**")  # Course Title
                st.write(f"Description: {course[2]}")
                st.write(f"Price: ${course[3]}")
                st.write("---")
        else:
            st.info('You have not enrolled in any courses yet.')

    def profile(self):
        st.subheader('Profile')
        st.write(f'Username: {st.session_state["username"]}')
        st.write(f'Email: {self.db.get_user_email(st.session_state["username"])}')
        st.write(f'Role: {st.session_state["user_role"]}')

    def manage_users(self):
        st.subheader('Manage Users')
        users = self.db.get_all_users()
        if users:
            for user in users:
                st.write(f"ID: {user[0]}, Username: {user[1]}, Email: {user[3]}, Role: {user[4]}")
                if st.button(f'Change Role for {user[1]}', key=user[0]):
                    new_role = st.selectbox(f'New role for {user[1]}', ['admin', 'student', 'instructor'], key=user[0])
                    if st.button('Update', key=user[0]):
                        self.db.update_user_role(user[0], new_role)
                        st.success(f'Role updated for {user[1]}')
        else:
            st.info('No users available.')

    def view_all_courses(self):
        st.subheader('All Courses')
        courses = self.db.get_all_courses()
        if courses:
            for course in courses:
                st.write(f"ID: {course[0]}, Title: {course[1]}, Instructor: {self.db.get_instructor_name(course[3])}")
        else:
            st.info('No courses available.')

    def system_statistics(self):
        st.subheader('System Statistics')
        st.write(f'Total Users: {self.db.get_total_users()}')
        st.write(f'Total Courses: {self.db.get_total_courses()}')
        st.write(f'Total Enrollments: {self.db.get_total_enrollments()}')

    def run(self):
        st.sidebar.title('Udemy Clone')

        if 'username' not in st.session_state:
            page = st.sidebar.radio('Navigation', ['Login', 'Register'])
            
            if page == 'Login':
                self.login_page()
            else:
                self.registration_page()
        else:
            st.sidebar.write(f'Welcome, {st.session_state["username"]}')
            
            if st.sidebar.button('Logout'):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

            if st.session_state['user_role'] == 'admin':
                self.admin_dashboard()
            elif st.session_state['user_role'] == 'student':
                self.student_dashboard()
            elif st.session_state['user_role'] == 'instructor':
                self.instructor_dashboard()

def main():
    app = UdemyClone()
    app.run()

if __name__ == '__main__':
    main()