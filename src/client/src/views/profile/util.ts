import { UseFormReturnType } from "@mantine/form";
import { UserProfileDto } from "../../models/dto/profile";
import { ProfileUpdatePayload } from "../../api/contracts";

export const mapInboundProfileData = (profile: UserProfileDto) => {
    return {
        ...profile,
        learning_capacities:
            profile.selected_learning_capacities || profile.learning_capacities,
        hobby: !!profile.hobby
            ? {
                  ...profile.hobby,
                  skills: profile.hobby.skills?.map(
                      (skill) =>
                          profile.skills.find((s) => s.id === skill)!.skill
                  ),
              }
            : null,
        student: !!profile.student
            ? {
                  ...profile.student,
                  schools: profile.student.schools?.map((school) => ({
                      ...school,
                      start_date: school.start_date
                          ? new Date(school.start_date)
                          : null,
                      end_date: school.end_date
                          ? new Date(school.end_date)
                          : null,
                      skills: school.skills.map(
                          (skill) =>
                              profile.skills.find((s) => s.id === skill)!.skill
                      ),
                  })),
              }
            : null,
        professional: !!profile.professional
            ? {
                  ...profile.professional,
                  employers: profile.professional.employers?.map(
                      (employer) => ({
                          ...employer,
                          start_date: employer.start_date
                              ? new Date(employer.start_date)
                              : null,
                          end_date: employer.end_date
                              ? new Date(employer.end_date)
                              : null,
                          skills: employer.skills.map(
                              (skill) =>
                                  profile.skills.find((s) => s.id === skill)!
                                      .skill
                          ),
                      })
                  ),
              }
            : null,
    };
};

export const mapOutboundProfileData = (
    form: UseFormReturnType<ProfileUpdatePayload>
) => {
    function formatDate(date: Date | string) {
        const dt = typeof date === "string" ? new Date(date) : date;
        const monthPadded = `${dt.getMonth() + 1}`.padStart(2, "0");
        const datePadded = `${dt.getDate()}`.padStart(2, "0");
        return `${dt.getFullYear()}-${monthPadded}-${datePadded}`;
    }

    return {
        ...form.values,
        student: form.values.student
            ? {
                  ...form.values.student,
                  schools: form.values.student.schools.map((school) => ({
                      ...school,
                      start_date: school.start_date
                          ? formatDate(school.start_date)
                          : null,
                      end_date: school.end_date
                          ? formatDate(school.end_date)
                          : null,
                  })),
              }
            : null,
        professional: form.values.professional
            ? {
                  ...form.values.professional,
                  employers: form.values.professional.employers.map(
                      (employer) => ({
                          ...employer,
                          start_date: employer.start_date
                              ? formatDate(employer.start_date)
                              : null,
                          end_date: employer.end_date
                              ? formatDate(employer.end_date)
                              : null,
                      })
                  ),
              }
            : null,
    };
};

export function mapCheckListField(
    form: UseFormReturnType<ProfileUpdatePayload>,
    field: string,
    options: any,
    inputProps: any
) {
    const { value } = options;

    function getValueFromDotPath(obj: any, path: string): any {
        // Support indexes too
        const parts = path.split(".");

        return parts.reduce((acc, part) => {
            if (part.includes("[")) {
                const [key, index] = part.split("[");

                if (!acc[key]) {
                    return null;
                }

                return acc[key][index.replace("]", "")];
            } else if (!isNaN(parseInt(part))) {
                return acc[parseInt(part)];
            }

            return acc[part];
        }, obj);
    }

    return {
        ...inputProps,
        onChange: (checked: boolean) => {
            if (checked) {
                console.log(`add ${value} to ${field}`);
                form.insertListItem(field, value);
            } else {
                console.log(`remove ${value} from ${field}`);
                form.removeListItem(field, value);
            }
        },
        checked: getValueFromDotPath(form.values, field)?.includes(value),
    };
}
