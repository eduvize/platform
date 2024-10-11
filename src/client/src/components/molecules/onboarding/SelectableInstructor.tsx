import { Avatar } from "@mantine/core";
import { InstructorDto } from "@models/dto";
const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

interface SelectableInstructorProps extends InstructorDto {
    selected?: boolean;
    onClick: () => void;
}

export const SelectableInstructor = ({
    id,
    name,
    selected,
    onClick,
}: SelectableInstructorProps) => {
    return (
        <Avatar
            size={128}
            src={`${apiEndpoint}/instructors/${id}/profile-photo`}
            onClick={onClick}
            alt={name}
            styles={{
                root: {
                    border: selected
                        ? "6px solid #8DCAFF"
                        : "6px solid transparent",
                },
            }}
        />
    );
};
