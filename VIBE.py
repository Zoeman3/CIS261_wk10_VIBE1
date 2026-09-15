#Zoe Miller
#CIS261
#VIBE Coding

"""Student gradebook with file storage and automatic grade calculations."""

import sys

FILE_NAME = "student_grades.txt"


def calculate_average(scores):
	"""Return the average of three test scores."""
	return sum(scores) / len(scores) if scores else 0.0


def calculate_letter_grade(average):
	"""Return the letter grade for an average percentage."""
	if average >= 90:
		return "A"
	if average >= 80:
		return "B"
	if average >= 70:
		return "C"
	if average >= 60:
		return "D"
	return "F"


class Student:
	"""Store one student's information and calculated grade."""

	def __init__(self, name, student_id, scores):
		self.name = name
		self.id = student_id
		self.test_scores = scores
		self.average = calculate_average(scores)
		self.grade = calculate_letter_grade(self.average)

	@property
	def scores(self):
		"""Provide the shorter name used by the table and input workflow."""
		return self.test_scores

	def to_dict(self):
		return {"name": self.name, "id": self.id, "scores": self.test_scores}

	@classmethod
	def from_dict(cls, record):
		return cls(record["name"], record["id"], record["scores"])


def save_students(students):
	"""Save all student records to the gradebook file."""
	try:
		with open(FILE_NAME, "w", encoding="utf-8") as file:
			for student in students:
				file.write(format_student_record(student))
		return True
	except OSError as error:
		print(f"Unable to save records to {FILE_NAME}: {error}")
		return False


def format_student_record(student):
	"""Return one student record in the required pipe-delimited format."""
	scores = "|".join(f"{score:.2f}" for score in student.test_scores)
	return f"{student.name}|{student.id}|{scores}|{student.average:.2f}|{student.grade}\n"


def load_students():
	"""Load student records, returning an empty list if the file is absent."""
	try:
		with open(FILE_NAME, encoding="utf-8") as file:
			students = []
			for line_number, line in enumerate(file, start=1):
				fields = line.strip().split("|")
				if len(fields) != 7:
					print(f"Skipping invalid record on line {line_number}.")
					continue
				try:
					name, student_id = fields[:2]
					scores = [float(score) for score in fields[2:5]]
					students.append(Student(name, student_id, scores))
				except ValueError:
					print(f"Skipping invalid scores on line {line_number}.")
			return students
	except FileNotFoundError:
		return []
	except OSError as error:
		print(f"Unable to load records from {FILE_NAME}: {error}")
		return []


def get_score(test_number):
	"""Read a valid score from 0 through 100."""
	while True:
		try:
			score = float(input(f"Test {test_number} score: "))
			if 0 <= score <= 100:
				return score
			print("Score must be between 0 and 100.")
		except ValueError:
			print("Please enter a number.")


def get_three_scores():
	return [get_score(number) for number in range(1, 4)]


def find_by_id(students, student_id):
	return next((student for student in students if student.id == student_id), None)


def print_table(students):
	"""Print all records in a formatted table."""
	if not students:
		print("No student records found.")
		return

	headers = ("Name", "Student ID", "Test 1", "Test 2", "Test 3", "Average", "Grade")
	rows = []
	for student in students:
		rows.append((
			student.name, student.id, *(f"{score:.2f}" for score in student.test_scores),
			f"{student.average:.2f}", student.grade,
		))

	widths = [max(len(str(row[index])) for row in [headers, *rows]) for index in range(len(headers))]
	separator = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
	print(separator)
	print("| " + " | ".join(f"{value:<{widths[index]}}" for index, value in enumerate(headers)) + " |")
	print(separator)
	for row in rows:
		print("| " + " | ".join(f"{value:<{widths[index]}}" for index, value in enumerate(row)) + " |")
	print(separator)


def display_class_summary(students):
	if not students:
		print("No student records found.")
		return
	averages = [(student, student.average) for student in students]
	highest = max(averages, key=lambda item: item[1])
	lowest = min(averages, key=lambda item: item[1])
	class_average = sum(average for _, average in averages) / len(averages)
	print(f"Highest average: {highest[0].name} ({highest[1]:.2f}%)")
	print(f"Lowest average:  {lowest[0].name} ({lowest[1]:.2f}%)")
	print(f"Class average:   {class_average:.2f}%")


def add_student(students):
	student_id = input("Student ID: ").strip()
	if not student_id or find_by_id(students, student_id):
		print("Student ID must be unique and cannot be blank.")
		return
	name = input("Student name: ").strip()
	if not name:
		print("Student name cannot be blank.")
		return
	students.append(Student(name, student_id, get_three_scores()))
	if save_students(students):
		print(f"Student {name} added and saved successfully.")
	else:
		print(f"Student {name} was added for this session, but could not be saved.")


def search_student(students):
	name = input("Enter student name (case sensitive): ")
	matches = [student for student in students if student.name == name]
	if matches:
		print_table(matches)
	else:
		print("No student found with that exact name.")


def read_menu_choice():
	"""Read one menu key so pressing Escape exits immediately."""
	if sys.platform == "win32":
		import msvcrt
		key = msvcrt.getwch()
	else:
		import termios
		import tty
		settings = termios.tcgetattr(sys.stdin)
		try:
			tty.setraw(sys.stdin.fileno())
			key = sys.stdin.read(1)
		finally:
			termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
	print(key if key != "\x1b" else "ESC")
	return key


def main():
	students = load_students()
	print(f"Loaded {len(students)} student record(s) from {FILE_NAME}.")
	while True:
		print("\nStudent Gradebook")
		print("1. Add student")
		print("2. Display all students")
		print("3. Display class summary")
		print("4. Search by student name")
		print("Press ESC to save and exit")
		choice = read_menu_choice()
		if choice == "1":
			add_student(students)
		elif choice == "2":
			print_table(students)
		elif choice == "3":
			display_class_summary(students)
		elif choice == "4":
			search_student(students)
		elif choice == "\x1b":
			if save_students(students):
				print("All records saved. Goodbye.")
			else:
				print("Goodbye. Records could not be saved.")
			break
		else:
			print("Choose 1, 2, 3, or 4.")


if __name__ == "__main__":
	main()