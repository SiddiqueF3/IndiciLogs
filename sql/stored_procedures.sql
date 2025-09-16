-- =============================================
-- Console Error Logs Web Application
-- SQL Server Stored Procedures
-- =============================================

-- 1. Stored Procedure to Retrieve Filtered Data
-- =============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[LOG].[sp_GetConsoleErrorLogs]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [LOG].[sp_GetConsoleErrorLogs]
GO

CREATE PROCEDURE [LOG].[sp_GetConsoleErrorLogs]
    @DateFrom DATETIME = NULL,
    @DateTo DATETIME = NULL,
    @TimeFrom VARCHAR(8) = NULL,
    @TimeTo VARCHAR(8) = NULL,
    @PracticeID VARCHAR(10) = NULL,
    @Page INT = 1,
    @PerPage INT = 25
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @TimeFromConv TIME = NULL;
    DECLARE @TimeToConv TIME = NULL;
    DECLARE @PracticeIDInt INT = NULL;

    IF (@TimeFrom IS NOT NULL AND LTRIM(RTRIM(@TimeFrom)) <> '')
        SET @TimeFromConv = TRY_CAST(@TimeFrom AS TIME);

    IF (@TimeTo IS NOT NULL AND LTRIM(RTRIM(@TimeTo)) <> '')
        SET @TimeToConv = TRY_CAST(@TimeTo AS TIME);

    IF (@PracticeID IS NOT NULL AND LTRIM(RTRIM(@PracticeID)) <> '')
        SET @PracticeIDInt = TRY_CAST(@PracticeID AS INT);

    IF (@Page IS NULL OR @Page < 1) SET @Page = 1;
    IF (@PerPage IS NULL OR @PerPage < 1) SET @PerPage = 25;

    ;WITH Filtered AS (
        SELECT
            id,
            practiceid,
            stacktraces,
            ErrorMassage,
            url,
            ErrorTime,
            insertdat,
            updatedat,
            JiraStatus,
            Status
        FROM LOG.tblconsoleErrorLogs
        WHERE
            (@DateFrom IS NULL OR CAST(insertdat AS DATE) >= @DateFrom)
            AND (@DateTo IS NULL OR CAST(insertdat AS DATE) <= @DateTo)
            AND (@TimeFrom IS NULL OR LTRIM(RTRIM(@TimeFrom)) = '' OR CAST(ErrorTime AS TIME) >= @TimeFromConv)
            AND (@TimeTo IS NULL OR LTRIM(RTRIM(@TimeTo)) = '' OR CAST(ErrorTime AS TIME) <= @TimeToConv)
            AND (@PracticeID IS NULL OR LTRIM(RTRIM(@PracticeID)) = '' OR practiceid = @PracticeIDInt)
    ), Numbered AS (
        SELECT
            *,
            ROW_NUMBER() OVER (ORDER BY ErrorTime DESC) AS RowNum,
            COUNT(1) OVER() AS TotalCount
        FROM Filtered
    )
    SELECT
        id,
        practiceid,
        stacktraces,
        ErrorMassage,
        url,
        ErrorTime,
        insertdat,
        updatedat,
        JiraStatus,
        Status,
        TotalCount
    FROM Numbered
    WHERE RowNum BETWEEN ((@Page - 1) * @PerPage + 1) AND (@Page * @PerPage)
    ORDER BY RowNum;
END;
GO

-- 2. Stored Procedure to Retrieve Practice IDs
-- =============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[LOG].[sp_GetPracticeIDs]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [LOG].[sp_GetPracticeIDs]
GO

CREATE PROCEDURE [LOG].[sp_GetPracticeIDs]
AS
BEGIN
    SET NOCOUNT ON;

    SELECT DISTINCT practiceid
    FROM [LOG].[tblconsoleErrorLogs]
    WHERE practiceid IS NOT NULL
    ORDER BY practiceid;
END;
GO

-- Grant permissions (adjust as needed for your environment)
-- GRANT EXECUTE ON [LOG].[sp_GetConsoleErrorLogs] TO [your_app_user];
-- GRANT EXECUTE ON [LOG].[sp_GetPracticeIDs] TO [your_app_user];

PRINT 'Stored procedures created successfully!';
