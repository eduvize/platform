interface Tool {
    name: string;
    data: any | null;
}

export interface CompletionChunkDto {
    message_id: string;
    received_text: string | null;
    text: string | null;
    audio?: string | null;
    tools: Tool[] | null;
}
