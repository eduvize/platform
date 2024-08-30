import { CourseApi } from "@api";
import { Box, Center, Loader, LoadingOverlay } from "@mantine/core";
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

    if (!course) {
        return (
            <Center h="100%">
                <Loader size="lg" type="dots" />
            </Center>
        );
    }

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
