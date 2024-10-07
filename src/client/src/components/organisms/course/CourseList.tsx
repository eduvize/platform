import { useCourses } from "@context/course/hooks";
import { Group } from "@mantine/core";
import { CourseListing } from "@molecules";
import { useNavigate } from "react-router-dom";

interface CourseListProps {
    onNewCourseClick: () => void;
}

export const CourseList = ({ onNewCourseClick }: CourseListProps) => {
    const navigate = useNavigate();
    const courses = useCourses();

    return (
        <Group p="lg" gap="xl">
            {courses.map((course) => (
                <CourseListing
                    key={course.id}
                    {...course}
                    onClick={() => {
                        navigate(`/dashboard/course/${course.id}`);
                    }}
                />
            ))}

            <CourseListing is_new onClick={onNewCourseClick} />
        </Group>
    );
};
