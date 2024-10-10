import { useChat } from "@context/chat";
import { Avatar, AvatarProps } from "@mantine/core";
const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

interface InstructorAvatarProps extends AvatarProps {}

export const InstructorAvatar = (props: InstructorAvatarProps) => {
    const { instructorId } = useChat();

    return (
        <Avatar
            {...props}
            src={`${apiEndpoint}/instructors/${instructorId}/profile-photo`}
        />
    );
};
