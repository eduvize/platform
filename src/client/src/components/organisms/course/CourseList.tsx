import { useCourses } from "@context/course/hooks";
import { Group } from "@mantine/core";
import { CourseListing } from "@molecules";
import { useNavigate } from "react-router-dom";

export const CourseList = () => {
    const navigate = useNavigate();
    const courses = useCourses();

    return (
        <Group p="lg">
            {courses.map((course) => (
                <CourseListing
                    key={course.id}
                    {...course}
                    onClick={() => {
                        navigate(`/dashboard/course/${course.id}`);
                    }}
                />
            ))}
        </Group>
    );
};
