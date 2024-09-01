## Course Creation

The course creation process starts with the user describing basic information regarding what they would like to learn. This information is used to generate follow-up questions that are more geared toward learning specifics around their relationship to the subject and more concrete details of what they would like to focus on. Once the user submits answers, a rough course outline is created along with a cover image and it is saved to the database. Afterwards, a message is produced to Kafka where a separate *course generation job* consumes it and works to fill out individual lesson content one module at a time. The user is able to see progress in real-time from their course catalog and, once fully generated, view the course.

Here is an illustration of this process:
![diagram-export-8-31-2024-9_28_20-AM](https://github.com/user-attachments/assets/83c01617-6519-4626-b7e8-3f947e4d3c45)

## The Anatomy of a Course

Courses are divided up into several components:

- **Module**: A distinct chapter in the course focusing on a particular subject
  - **Lessons**: A series of focused sub-topics that roll up to the primary objective of a module
    - **Lesson**: A specific sub-topic
      - **Section**: Used to break up lessons into a more digestible form
    - **Exercise**: Optional hands-on exercise for the user to apply what they just learned
  - **Quiz**: An end-of-module comprehension quiz
- **Project**: If applicable, a final project that incorporates the core subjects of the course

### Lessons

Lessons contain the core reading material. In addition to reading, the user may engage with their AI tutor to ask clarifying questions about the content, which is taken into account in the development of exercises, quizzes and projects.

### Exercises

An exercise allows users to apply the learnings from a lesson in a sandboxed environment, enabling them to get hands-on from the beginning and without requiring them to have any tools installed on their machine. These environments are seeded with all of the material they will need in order to complete the objective.

Additionally, Eduvize will track the user's interactions with the environment, and outputs, in order to determine how the user is performing the task. These notes will be leveraged within end-of-module comprehension quizzes and a final project to ensure progression.

**Quizzes**

A quiz is a series of questions about the main takeaways from a particular learning module. Quizzes can contain multiple choice and free text entry inputs.

**Project**

An end-of-course project takes all of the main learning points of a course, and other user comprehension feedback, into account in order to develop project requirements and objectives. The user is given an editor environment and is expected to meet criteria of a rubric in order to complete the course.
