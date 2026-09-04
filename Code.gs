const SPREADSHEET_ID = "1QreeVlM379CLvLCoDHAZunzp9tIwwPkQ9LrQUK0ukgE";
const SHEET_NAME = "Sheet1";
const DRIVE_FOLDER_ID = "1Fl0r5cZFPeWL6Fjhz9uLh2vTuzXfaJV9";

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = spreadsheet.getSheetByName(SHEET_NAME);

    if (!sheet) {
      throw new Error("Sheet not found: " + SHEET_NAME);
    }

    const folder = DriveApp.getFolderById(DRIVE_FOLDER_ID);

    const resumeBytes = Utilities.base64Decode(data.resume_base64);

    const resumeBlob = Utilities.newBlob(
      resumeBytes,
      data.resume_type,
      data.resume_name
    );

    const resumeFile = folder.createFile(resumeBlob);
    const resumeLink = resumeFile.getUrl();

    sheet.appendRow([
      data.candidate_id,
      data.timestamp,
      data.full_name,
      data.mobile,
      data.email,
      data.aadhaar,
      data.pan,
      data.current_city,
      data.highest_qualification,
      data.institute,
      data.graduation_year,
      data.cgpa_percentage,
      data.experience_type,
      data.total_experience,
      data.relevant_experience,
      data.current_company,
      data.current_designation,
      data.notice_period,
      data.primary_skill,
      resumeLink
    ]);

    return ContentService
      .createTextOutput(
        JSON.stringify({
          success: true,
          candidate_id: data.candidate_id,
          resume_link: resumeLink
        })
      )
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService
      .createTextOutput(
        JSON.stringify({
          success: false,
          message: error.toString()
        })
      )
      .setMimeType(ContentService.MimeType.JSON);
  }
}
