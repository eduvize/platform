export interface StudentDto {
    schools: SchoolDto[];
}

export interface SchoolDto {
    school_name: string;
    focus?: string;
    start_date: string | Date | null;
    end_date?: string | Date | null;
    is_current: boolean;
    did_finish: boolean;
    skills: string[];
}
