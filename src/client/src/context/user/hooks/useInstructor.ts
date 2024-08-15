import { useEffect, useState } from "react";
import { InstructorDto } from "@models/dto";
import { InstructorApi } from "@api";

export const useInstructor = (): [
    InstructorDto | null,
    (animal: string) => void,
    () => Promise<void>
] => {
    const [instructor, setInstructor] = useState<InstructorDto | null>(null);

    useEffect(() => {
        getInstructor();
    }, []);

    const getInstructor = () => {
        InstructorApi.getInstructor()
            .then((response) => {
                setInstructor(response);
            })
            .catch(() => {
                setInstructor(null);
            });
    };

    const generateInstructor = (animal: string) => {
        InstructorApi.generateInstructor(animal)
            .then((response) => {
                setInstructor(response);
            })
            .catch(() => {
                setInstructor(null);
            });
    };

    return [instructor, generateInstructor, () => InstructorApi.approve()];
};
