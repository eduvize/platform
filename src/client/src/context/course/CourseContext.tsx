import { CourseApi } from "@api";
import { Box, LoadingOverlay } from "@mantine/core";
import { CourseDto } from "@models/dto";
import { useEffect, useState } from "react";
import { createContext } from "use-context-selector";

type Context = {
    course: CourseDto | null;
};

const defaultValue: Context = {
    course: null,
};

export const CourseContext = createContext<Context>(defaultValue);

interface CourseProviderProps {
    courseId: string;
    children: React.ReactNode;
}

export const CourseProvider = ({ courseId, children }: CourseProviderProps) => {
    const [course, setCourse] = useState<CourseDto | null>(null);

    useEffect(() => {
        CourseApi.getCourse(courseId).then((course) => {
            setCourse(course);
        });
    }, [courseId]);

    return (
        <CourseContext.Provider
            value={{
                course,
            }}
        >
            <Box pos="relative">
                <LoadingOverlay
                    visible={course === null}
                    loaderProps={{
                        type: "bars",
                    }}
                />

                {children}
            </Box>
        </CourseContext.Provider>
    );
};
