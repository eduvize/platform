import { useContext } from "use-context-selector";
import { AudioInputContext } from "../AudioInputContext";

export const useAudioInput = () => {
    const {
        isListening,
        isSpeaking,
        startListening,
        stopListening,
        audioBuffer,
        sampleRate,
    } = useContext(AudioInputContext);

    return {
        isListening,
        isSpeaking,
        startListening,
        stopListening,
        audioBuffer,
        sampleRate,
    };
};
