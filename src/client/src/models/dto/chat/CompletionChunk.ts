interface Tool {
    name: string;
    data: any | null;
}

export interface CompletionChunkDto {
    message_id: string;
    text: string | null;
    tools: Tool[] | null;
}
