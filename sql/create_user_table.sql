-- =============================================
-- Console Log User Table Creation Script
-- =============================================

-- Create ConsoleLogUser table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ConsoleLogUser]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[ConsoleLogUser] (
        [Id] INT IDENTITY(1,1) NOT NULL,
        [Username] NVARCHAR(50) NOT NULL,
        [Password] NVARCHAR(255) NOT NULL,
        [Email] NVARCHAR(100) NULL,
        [FullName] NVARCHAR(100) NULL,
        [IsActive] BIT NOT NULL DEFAULT 1,
        [CreatedDate] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [LastLoginDate] DATETIME2 NULL,
        [Role] NVARCHAR(20) NOT NULL DEFAULT 'User',
        CONSTRAINT [PK_ConsoleLogUser] PRIMARY KEY CLUSTERED ([Id] ASC)
    );
    
    PRINT 'ConsoleLogUser table created successfully!';
END
ELSE
BEGIN
    PRINT 'ConsoleLogUser table already exists.';
END
GO

-- Create unique index on Username
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID(N'[dbo].[ConsoleLogUser]') AND name = N'IX_ConsoleLogUser_Username')
BEGIN
    CREATE UNIQUE NONCLUSTERED INDEX [IX_ConsoleLogUser_Username] 
    ON [dbo].[ConsoleLogUser] ([Username] ASC);
    
    PRINT 'Unique index on Username created successfully!';
END
GO

-- Insert default admin user (password: admin123)
IF NOT EXISTS (SELECT 1 FROM [dbo].[ConsoleLogUser] WHERE [Username] = 'admin')
BEGIN
    INSERT INTO [dbo].[ConsoleLogUser] ([Username], [Password], [Email], [FullName], [Role])
    VALUES ('admin', 'admin123', 'admin@consolelogs.com', 'Administrator', 'Admin');
    
    PRINT 'Default admin user created successfully!';
    PRINT 'Username: admin, Password: admin123';
END
ELSE
BEGIN
    PRINT 'Default admin user already exists.';
END
GO

-- Create stored procedure for user login
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_ConsoleLogUser_Login]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_ConsoleLogUser_Login]
GO

CREATE PROCEDURE [dbo].[sp_ConsoleLogUser_Login]
    @Username NVARCHAR(50),
    @Password NVARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @UserId INT = NULL;
    DECLARE @IsValid BIT = 0;
    DECLARE @UserRole NVARCHAR(20) = NULL;
    DECLARE @FullName NVARCHAR(100) = NULL;
    
    -- Check if user exists and password matches
    SELECT 
        @UserId = Id,
        @UserRole = Role,
        @FullName = FullName
    FROM [dbo].[ConsoleLogUser]
    WHERE [Username] = @Username 
        AND [Password] = @Password 
        AND [IsActive] = 1;
    
    -- If user found, update last login date
    IF @UserId IS NOT NULL
    BEGIN
        UPDATE [dbo].[ConsoleLogUser]
        SET [LastLoginDate] = GETDATE()
        WHERE [Id] = @UserId;
        
        SET @IsValid = 1;
    END
    
    -- Return login result
    SELECT 
        @IsValid AS IsValid,
        @UserId AS UserId,
        @Username AS Username,
        @UserRole AS Role,
        @FullName AS FullName;
END
GO

PRINT 'Login stored procedure created successfully!';
PRINT 'Use: EXEC [dbo].[sp_ConsoleLogUser_Login] @Username = ''admin'', @Password = ''admin123''';
