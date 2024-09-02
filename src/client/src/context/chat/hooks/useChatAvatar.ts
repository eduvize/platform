import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";

export const useChatAvatar = (side: "remote" | "local"): string | null => {
    const remoteAvatar = ""; // TODO
    const localAvatar = useContextSelector(
        ChatContext,
        (v) => v.localPartyAvatarUrl
    );

    return side === "remote" ? remoteAvatar : localAvatar;
};
