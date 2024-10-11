import { useInstructors } from "@hooks/instructors";
import { Avatar, Group, Stack } from "@mantine/core";
const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

export const Instructors = () => {
    const instructors = useInstructors();

    return (
        <Stack>
            <Group>
                {instructors.map(({ id }) => (
                    <Avatar
                        key={id}
                        src={`${apiEndpoint}/instructors/${id}/profile-photo`}
                    />
                ))}
            </Group>
        </Stack>
    );
};
