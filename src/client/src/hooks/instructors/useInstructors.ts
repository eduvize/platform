import { InstructorApi } from "@api";
import { InstructorDto } from "@models/dto";
import { useEffect, useState } from "react";

export const useInstructors = () => {
    const [instructors, setInstructors] = useState<InstructorDto[]>([]);

    useEffect(() => {
        InstructorApi.getInstructors().then(setInstructors);
    }, []);

    return instructors;
};
